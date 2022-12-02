#!/usr/bin/env python3

import os
import base64
import hashlib
import io
import uuid
import tempfile

import jsonpickle
from app import app
from app.config import Config
from app.client import minioClient, redisClient
from app.db import db_connection, User, Passwords
from flask import make_response, request, send_file, render_template
from flask.wrappers import Response
from werkzeug.utils import secure_filename

import minio
import sqlalchemy

__version__ = "api/v1"


def generate_nonc_uuid():
    while True:
        gen_id = str(uuid.uuid4())
        query = sqlalchemy.select([sqlalchemy.func.count()]).where(
            User.columns.userId == gen_id)
        collision = db_connection.execute(query)
        if collision != 1:
            return gen_id


def save_file_to_minio(bucket, filename, data, size):
    try:
        minioClient.stat_object(bucket, filename)
        reason = "file already uploaded"
        app.logger.warn(reason)
    except minio.error.S3Error as e:
        if e.code == "NoSuchKey":
            app.logger.info(f"Adding {filename} to the bucket")
            try:
                minioClient.put_object(
                    bucket, filename, data, length=size)
            except Exception as e2:
                app.logger.error("Error adding file to the bucket")
                reason = "Failed to parse the file"
                app.logger.warn(reason, e2)
                raise e2
        else:
            reason = "Failed to upload"
            app.logger.error(reason, e)
            raise e
    except Exception as e:
        reason = "Failed to upload"
        app.logger.error(reason, e)
        raise e


@app.route(f"/{__version__}/crack", methods=["POST"])
def crack():
    # gen_id = generate_nonc_uuid()
    gen_id = "abc"

    _, tempfile_path = tempfile.mkstemp()
    hashFile = f'{gen_id}'
    try:
        inputType = request.form.get('inputType')
        if inputType == 'file':
            request_file = request.files.get('hashFile')
            print(request_file)
            if not request_file or request_file.filename == '':
                task = {'error': "Input hash file not uploaded"}
                jsonRes = jsonpickle.encode(task)
                return Response(response=jsonRes, status=400, mimetype="application/json")

            request_file.save(tempfile_path)
            size = os.stat(tempfile_path).st_size
            if size == 0:
                task = {'error': "Empty file"}
                jsonRes = jsonpickle.encode(task)
                return Response(response=jsonRes, status=400, mimetype="application/json")

        elif inputType == 'text':
            text = request.form.get('inputText')
            if not text or len(text) == 0:
                task = {'error': "Empty text"}
                jsonRes = jsonpickle.encode(task)
                return Response(response=jsonRes, status=400, mimetype="application/json")
            with open(tempfile_path) as file:
                file.write(text)

        else:
            task = {'error': "Invalid inputType"}
            jsonRes = jsonpickle.encode(task)
            return Response(response=jsonRes, status=400, mimetype="application/json")

        size = os.stat(tempfile_path).st_size
        with open(tempfile_path, mode='r') as file:
            try:
                save_file_to_minio(Config.INPUT_BUCKET, hashFile, file, size)
            except Exception as e:
                task = {'error': "Failed to save the hash file"}
                jsonRes = jsonpickle.encode(task)
                return Response(response=jsonRes, status=500, mimetype="application/json")
    finally:
        os.remove(tempfile_path)

    hashType = request.form.get('hashType')
    crackingMode = request.form.get('crackingType')
    wordlist = request.form.get('wordlist')

    task = {}
    task["id"] = gen_id

    insert_query = (
        sqlalchemy.insert(User).values(
            userId=gen_id,
            crackingMode=crackingMode,
            hashFile=hashFile,
            wordlistFile=wordlist,
            hashType=hashType)
    )
    # print(insert_query)
    db_connection.execute(insert_query)

    redisClient.lpush(Config.WORK_KEY, gen_id)

    jsonRes = jsonpickle.encode(task)
    return Response(response=jsonRes, status=200, mimetype="application/json")


@app.route(f"/{__version__}/wordlist", methods=["GET"])
def list_wordlist():
    wordlist = []
    wordlist.append("aaaa")
    wordlist.append("bbb")
    jsonRes = jsonpickle.encode(wordlist)
    return Response(response=jsonRes, status=200, mimetype="application/json")


@app.route(f"/{__version__}/task-details", methods=["GET"])
def get_task_details():
    taskId = request.args.get('taskId')
    if taskId == None:
        err = {'error': 'Empty taskID'}
        jsonRes = jsonpickle.encode(err)
        return Response(response=jsonRes, status=400, mimetype="application/json")

    task = {
        'id': taskId,
        'passwords': []
    }

    query = sqlalchemy.select([Passwords]).where(
        Passwords.columns.userId == taskId)
    res = db_connection.execute(query).fetchall()
    for row in res:
        pwd = {
            'hash': row[1],
            'password': row[2],
            'hash_type': row[3],
            'salt': row[4]
        }
        task['passwords'].append(pwd)

    jsonRes = jsonpickle.encode(task)
    return Response(response=jsonRes, status=200, mimetype="application/json")


@app.route(f"/{__version__}/pending-task", methods=["GET"])
def list_tasks():
    tasklist = []
    for x in redisClient.lrange(Config.WORK_KEY, 0, -1):
        tasklist.append(x.decode('utf-8'))
    jsonRes = jsonpickle.encode(tasklist)
    return Response(response=jsonRes, status=200, mimetype="application/json")


@app.route("/favicon.ico")
def logo():
    # https://www.iconfinder.com/icons/111039/key_icon
    return send_file('key_icon.png')


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def hello(path):
    return render_template("index.html", name="abc")