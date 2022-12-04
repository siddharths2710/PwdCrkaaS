#!/usr/bin/env python3

import os
import uuid
import tempfile

import jsonpickle
from app import app
from app.config import Config
from app.client import minioClient, redisClient
from app.db import db_connection, User, Passwords
from flask import request, send_file, render_template
from flask.wrappers import Response

import minio
import sqlalchemy

__version__ = "api/v1"

app.logger.info("Starting server")

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
    gen_id = generate_nonc_uuid()

    _, tempfile_path = tempfile.mkstemp()
    hashFile = f'{gen_id}'
    try:
        inputType = request.form.get('inputType')
        if inputType == 'file':
            request_file = request.files.get('hashFile')
            print(request_file)
            if not request_file or request_file.filename == '':
                task = {'error': "Input hash file not uploaded",
                        'name': 'hashFile'}
                jsonRes = jsonpickle.encode(task)
                return Response(response=jsonRes, status=400, mimetype="application/json")

            request_file.save(tempfile_path)
            size = os.stat(tempfile_path).st_size
            if size == 0:
                task = {'error': "Hash file provided is empty",
                        'name': 'hashFile'}
                jsonRes = jsonpickle.encode(task)
                return Response(response=jsonRes, status=400, mimetype="application/json")

        elif inputType == 'text':
            text = request.form.get('hashText')
            if not text or len(text) == 0:
                task = {'error': "The hash text is empty", 'name': 'hashText'}
                jsonRes = jsonpickle.encode(task)
                return Response(response=jsonRes, status=400, mimetype="application/json")
            with open(tempfile_path, mode='w') as file:
                file.write(text)

        else:
            task = {'error': "Invalid inputType", 'name': 'inputType'}
            jsonRes = jsonpickle.encode(task)
            return Response(response=jsonRes, status=400, mimetype="application/json")

        size = os.stat(tempfile_path).st_size
        with open(tempfile_path, mode='rb') as file:
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
    wordlist = ''
    if crackingMode == 'wordlist':
        wordlist = request.form.get('wordlist')
        if wordlist == '':
            task = {'error': "Wordlist is empty", 'name': 'wordlist'}
            jsonRes = jsonpickle.encode(task)
            return Response(response=jsonRes, status=500, mimetype="application/json")
        all_wordlist = get_wordlist()
        if wordlist not in all_wordlist:
            task = {'error': "Wordlist is not a valid selection",
                    'name': 'wordlist'}
            jsonRes = jsonpickle.encode(task)
            return Response(response=jsonRes, status=500, mimetype="application/json")

    task = {}
    task["id"] = gen_id

    with db_connection.begin():
        insert_query = (
            sqlalchemy.insert(User).values(
                userId=gen_id,
                crackingMode=crackingMode,
                hashFile=hashFile,
                wordlistFile=wordlist,
                hashType=hashType)
        )
        db_connection.execute(insert_query)

    redisClient.lpush(Config.WORK_KEY, gen_id)

    jsonRes = jsonpickle.encode(task)
    return Response(response=jsonRes, status=200, mimetype="application/json")


def get_wordlist():
    all_wordlist = []
    for wordlist in minioClient.list_objects(Config.WORDLIST_BUCKET):
        all_wordlist.append(wordlist.object_name)
    return all_wordlist

@app.route(f"/{__version__}/wordlist", methods=["GET"])
def list_wordlist():
    all_wordlist = get_wordlist()
    jsonRes = jsonpickle.encode(all_wordlist)
    return Response(response=jsonRes, status=200, mimetype="application/json")


@app.route(f"/{__version__}/task-details", methods=["GET", "POST"])
def get_task_details():
    taskId = request.args.get('taskId')
    if taskId == None:
        err = {'error': 'Empty taskID'}
        jsonRes = jsonpickle.encode(err)
        return Response(response=jsonRes, status=400, mimetype="application/json")

    status = ''
    query = sqlalchemy.select([User.columns.status]).where(
        User.columns.userId == taskId)
    res = db_connection.execute(query).fetchall()
    if len(res) != 1:
        err = {'error': f'Task "{taskId}" not found'}
        jsonRes = jsonpickle.encode(err)
        return Response(response=jsonRes, status=404, mimetype="application/json")
    else:
        status = res[0][0]

    task = {
        'id': taskId,
        'passwords': [],
        'status': status
    }

    # app.logger.warn("Starting passwords query")
    query = Passwords.select().where(Passwords.columns.userId == taskId)
    res = db_connection.execute(query).fetchall()
    for row in res:
        pwd = {
            'hash': row[1],
            'password': row[2],
            'hash_type': row[3],
            'salt': row[4]
        }
        task['passwords'].append(pwd)
        # app.logger.warn(f"Password is {pwd}")
    # app.logger.warn(f"Done with passwords")

    jsonRes = jsonpickle.encode(task)
    return Response(response=jsonRes, status=200, mimetype="application/json")


@app.route(f"/{__version__}/terminate-task", methods=["GET"])
def terminate_task():
    taskId = request.args.get('taskId')
    if taskId == None:
        err = {'error': 'Empty taskID'}
        jsonRes = jsonpickle.encode(err)
        return Response(response=jsonRes, status=400, mimetype="application/json")

    query = sqlalchemy.select([User.columns.status]).where(
        User.columns.userId == taskId)
    res = db_connection.execute(query).fetchall()
    if len(res) != 1:
        err = {'error': f'Task "{taskId}" not found'}
        jsonRes = jsonpickle.encode(err)
        return Response(response=jsonRes, status=404, mimetype="application/json")

    redisClient.lpush(Config.TERMINATE_KEY, taskId)

    task = {
        'id': taskId,
    }

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
