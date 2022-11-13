print("Worker Init")

import os
import sys
import glob
import time
import redis
import minio
import shutil
import platform
import tempfile
import subprocess
import minio.error
from enum import Enum

__author__ = "Siddharth Srinivasan"

"""
1. Read worker queue from redis; get hash
2. Borrow song from queue bucket in minio, and write to tempfile
3. Run demucs against song
4. Transfer output songs back to minio
"""
redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = int(os.getenv("REDIS_PORT") or "6379")

INPUT_BUCKET_NAME = os.getenv("INPUT_BUCKET_NAME") or 'lab7-queue'
OUTPUT_BUCKET_NAME = os.getenv("OUTPUT_BUCKET_NAME") or 'lab7-output'

class LOGLEVEL(Enum):
    INFO = 0
    DEBUG = 1
    ERROR = 2

redisHost, redisPort = os.getenv("REDIS_HOST") or "localhost", int(os.getenv("REDIS_PORT") or "6379")
minioHost, minioPort = os.getenv("MINIO_HOST") or "localhost", int(os.getenv("MINIO_PORT") or "9000")
minioUser, minioPwd = os.getenv('MINIO_USER') or "rootuser", os.getenv('MINIO_PWD') or "rootpass123"

logKey = "{}.worker.info".format(platform.node())
log_level = LOGLEVEL.INFO

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
minioClient = minio.Minio(f"{minioHost}:{minioPort}",
               access_key=minioUser,
               secret_key=minioPwd, secure=False)

def log_output(message, key=logKey, log_level=log_level):
    print("Worker", log_level.name, ":", message, file=sys.stdout)
    redisClient.lpush('logging', f"Worker:{log_level.name}:{key}:{message}")

log_output("Started Worker pod")

try:
    if not minioClient.bucket_exists(OUTPUT_BUCKET_NAME): minioClient.make_bucket(OUTPUT_BUCKET_NAME)
    while not minioClient.bucket_exists(INPUT_BUCKET_NAME):
                log_output(f"{INPUT_BUCKET_NAME}: Not created")
                time.sleep(1000)
                continue
except minio.error.S3Error as e: log_output(f"{OUTPUT_BUCKET_NAME} creation error: " + repr(e), log_level=LOGLEVEL.ERROR)
except minio.error.InvalidResponseError as e: log_output("MinIO API Error: " + repr(e), log_level=LOGLEVEL.ERROR)
except Exception as e: log_output("Error: " + repr(e), log_level=LOGLEVEL.ERROR)

while True:
        work = redisClient.blpop("toWorker", timeout=0)
        mp3_hash = work[1].decode('utf-8')
        log_output(f"Received {mp3_hash} for separation")
        try:
            dir_path = tempfile.mkdtemp()
            mp3_path, output_path = os.path.join(dir_path, f"{mp3_hash}.mp3"), os.path.join(dir_path, "output")
            os.mkdir(output_path)
            minioClient.fget_object(INPUT_BUCKET_NAME, mp3_hash, mp3_path)
            log_output("Running demucs separation utility")
            result = subprocess.run(["python3", "-m", "demucs.separate", "--mp3", "--out", output_path, mp3_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode:
                log_output(f"Demucs separate failure: {result.stdout.decode('utf-8')}: {result.stderr.decode('utf-8')}", log_level=LOGLEVEL.ERROR)
                continue

            for path, subdirs, files in os.walk(output_path):
                for name in files:
                    output_file = os.path.join(path, name)
                    minio_output_name = f"{mp3_hash}/{name}"
                    log_output(f"Got output {name} for {minio_output_name}")
                    minioClient.fput_object(
                        OUTPUT_BUCKET_NAME, minio_output_name, output_file, content_type="audio/mpeg")
            shutil.rmtree(dir_path)
        except minio.error.S3Error as e: log_output("MinIO Bucket/File Operation Failure: " + repr(e), log_level=LOGLEVEL.ERROR)
        except minio.error.InvalidResponseError as e: log_output("MinIO API Error: " + repr(e), log_level=LOGLEVEL.ERROR)
        except Exception as e: log_output("Error: " + repr(e), log_level=LOGLEVEL.ERROR)
