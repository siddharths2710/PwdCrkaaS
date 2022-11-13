#!/usr/bin/env python3

import os
import sys
import base64
import logging
import redis
import minio
import platform
import jsonpickle
import hashlib
import tempfile
import minio.error
from enum import Enum
from flask import Flask, request, make_response, Response

__author__ = "Siddharth Srinivasan"
__version__ = "apiv1"

ap = Flask(__name__)

INPUT_BUCKET_NAME = os.getenv("INPUT_BUCKET_NAME") or 'lab7-queue'
OUTPUT_BUCKET_NAME = os.getenv("OUTPUT_BUCKET_NAME") or 'lab7-output'
TRACK_TYPES = {"bass" , "vocals", "drums", "other"}

class LOGLEVEL(Enum):
    INFO = 0
    DEBUG = 1
    ERROR = 2

redisHost, redisPort = os.getenv("REDIS_HOST") or "localhost", int(os.getenv("REDIS_PORT") or "6379")
minioHost, minioPort = os.getenv("MINIO_HOST") or "localhost", int(os.getenv("MINIO_PORT") or "9000")
minioUser, minioPwd = os.getenv('MINIO_USER') or "rootuser", os.getenv('MINIO_PWD') or "rootpass123"

logKey = "{}.rest.info".format(platform.node())
log_level = LOGLEVEL.INFO

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
minioClient = minio.Minio(f"{minioHost}:{minioPort}",
               access_key=minioUser,
               secret_key=minioPwd, secure=False)

def log_output(message, key=logKey, log_level=log_level):
    print(log_level.name, ":", message, file=sys.stdout)
    redisClient.lpush('logging', f"REST:{log_level.name}:{key}:{message}")

try: 
    if not minioClient.bucket_exists(INPUT_BUCKET_NAME): minioClient.make_bucket(INPUT_BUCKET_NAME)
except minio.error.S3Error as e: log_output("Bucket/File creation error: " + repr(e), log_level=LOGLEVEL.ERROR)
except minio.error.InvalidResponseError as e: log_output("MinIO API Error: " + repr(e), log_level=LOGLEVEL.ERROR)
except Exception as e: log_output("MinIO API Error: " + repr(e), log_level=LOGLEVEL.ERROR)

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)

@app.route('/', methods=['GET']) #For GKE Health Check
def hello():
    return '<h1> Music Separation Server</h1><p> Use a valid endpoint </p>'

@app.route(f"/{__version__}/separate", methods=["POST"])
def separate():
    request_data = request.json
    mp3_data = base64.b64decode(request_data['mp3'].encode('utf-8'))
    mp3_hash = hashlib.sha256(mp3_data).hexdigest()
    status, reason = 200, "Success"
    try:
        minioClient.stat_object(INPUT_BUCKET_NAME, mp3_hash)
    except minio.error.S3Error as e:
        try:
            song_fd, song_path = tempfile.mkstemp()
            tmp = os.fdopen(song_fd, 'wb')
            tmp.write(mp3_data)
            tmp.close()
            minioClient.fput_object(INPUT_BUCKET_NAME, mp3_hash, song_path, content_type="audio/mpeg")
            os.remove(song_path)
            redisClient.lpush('toWorker', mp3_hash)
        except minio.error.S3Error as e: log_output("Bucket/File creation error: " + repr(e), log_level=LOGLEVEL.ERROR)
        except minio.error.InvalidResponseError as e: log_output("MinIO API Error: " + repr(e), log_level=LOGLEVEL.ERROR)
        except Exception as e: log_output("Error adding mp3 to bucket: " + repr(e), log_level=LOGLEVEL.ERROR)
    else:
        status, reason = 403, "Song already exists"

    """
    Check if bucket hash exists in minio
    """
    
    response = { 'hash': mp3_hash, "reason": reason }
    return Response(response=jsonpickle.encode(response), status=status, mimetype="application/json")


@app.route(f"/{__version__}/queue", methods=['GET'])
def queue():
    response = {"queue": [hash.decode('utf-8') for hash in redisClient.lrange("toWorker", 0, redisClient.llen("toWorker") - 1)]}
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

@app.route(f"/{__version__}/track/<songhash>/<track>", methods=['GET'])
def get_track(songhash, track):
    if track not in TRACK_TYPES:
        status, reason = 403, "Invalid Track type provided"
        response = {"reason": reason}
        if log_level == LOGLEVEL.DEBUG: log_output(f"{songhash}/track: {reason}")
        return Response(response=jsonpickle.encode(response), status=status, mimetype="application/json")
    try:
        song_bucket_path = f"{songhash}/{track}.mp3"
        song_fd, song_local_path = tempfile.mkstemp()
        stat_res = minioClient.fget_object(OUTPUT_BUCKET_NAME, song_bucket_path, song_local_path)
        
        tmp = os.fdopen(song_fd, 'rb')
        mp3_data = tmp.read()
        tmp.close()

        response = make_response(mp3_data)
        response.headers.set('Content-Type', "audio/mpeg")
        response.headers.set('Content-Disposition', 'attachment', filename='%s_%s.mp3' % (songhash, track))
        return response
    except minio.error.S3Error as e:
        status, reason = 404, "Either song still under processing, OR hash is invalid"
        response = {"reason": reason}
        log_output(f"Get {songhash}/{track}: {reason}", log_level=LOGLEVEL.ERROR)
        return Response(response=jsonpickle.encode(response), status=status, mimetype="application/json")
    except minio.error.InvalidResponseError as e: log_output("MinIO API Error: " + repr(e), log_level=LOGLEVEL.ERROR)
    except Exception as e: log_output("Error: " + repr(e), log_level=LOGLEVEL.ERROR)

@app.route(f"/{__version__}/remove/<songhash>/<track>", methods=['DELETE'])
def remove_track(songhash, track):
    if track not in TRACK_TYPES:
        status, reason = 403, "Invalid Track type provided"
        response = {"reason": reason}
        if log_level == LOGLEVEL.DEBUG: log_output(f"{songhash}/track: {reason}")
        return Response(response=jsonpickle.encode(response), status=status, mimetype="application/json")
    try:
        song_bucket_path = f"{songhash}/{track}.mp3"
        minioClient.remove_object(OUTPUT_BUCKET_NAME, song_bucket_path)
        status, reason = 200, f"{song_bucket_path} removal succeeded"
        response = {"reason": reason}
        return Response(response=jsonpickle.encode(response), status=status, mimetype="application/json")
    except minio.error.S3Error as e:
        status, reason = 404, "Either song still under processing, OR hash is invalid"
        response = {"reason": reason}
        log_output(f"Remove {songhash}/{track}: {reason}", log_level=LOGLEVEL.ERROR)
        return Response(response=jsonpickle.encode(response), status=status, mimetype="application/json")
    except minio.error.InvalidResponseError as e: log_output("MinIO API Error: " + repr(e), log_level=LOGLEVEL.ERROR)
    except Exception as e: log_output("Error: " + repr(e), log_level=LOGLEVEL.ERROR)

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
