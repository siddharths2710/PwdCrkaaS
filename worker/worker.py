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
import pandas as pd
from enum import Enum
import sqlalchemy as db

__author__ = "Siddharth Srinivasan"

"""
1. Read worker queue from redis; get hash
2. Borrow song from queue bucket in minio, and write to tempfile
3. Run demucs against song
4. Transfer output songs back to minio
"""
redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = int(os.getenv("REDIS_PORT") or "6379")

WORK_KEY, TERMINATE_KEY = "toWorker", 'toTerminate'
INPUT_BUCKET_NAME = os.getenv("INPUT_BUCKET_NAME") or 'lab7-queue'
OUTPUT_BUCKET_NAME = os.getenv("OUTPUT_BUCKET_NAME") or 'lab7-output'
JOHN_OUTPUT_FILE = os.path.join(os.path.expanduser('~'), '.john/john.pot')


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

mysql_db = os.getenv('MYSQL_DB') or 'foo'
mysql_uri = os.getenv('MYSQL_URI') or 'localhost'
mysql_user = os.getenv('MYSQL_USER') or 'scott'
mysql_pwd = os.getenv('MYSQL_PWD') or 'tiger'
db_engine = db.create_engine(f"mysql://{mysql_user}:{mysql_pwd}@{mysql_uri}/{mysql_db}")
db_connection = db_engine.connect()

# https://stackoverflow.com/questions/33053241/sqlalchemy-if-table-does-not-exist


# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_creating_table.htm
# https://towardsdatascience.com/sqlalchemy-python-tutorial-79a577141a91
meta = db.MetaData()
Password_Outputs = db.Table(
    'password_outputs', meta,
    db.Column('userId', db.Integer, primary_key=True, nullable=False),
    db.Column('hash', db.String, primary_key=True, nullable=False),
    db.Column('password', db.String, nullable=False),
    db.Column('hash_type', db.String, primary_key=True, nullable=False),
    db.Column('salt', db.String, nullable=False)
)

if not db_engine.dialect.has_table(db_connection, 'password_outputs'): meta.create_all(db_engine)

id_hash_map = {}
id_process_map = {}

def _get_user_id(pwd_hash):
    for user_id in id_hash_map:
        if pwd_hash in id_hash_map[user_id]:
            return user_id
    return None

def _handle_termination(terminate_id):
    if terminate_id not in id_process_map: redisClient.lpush(TERMINATE_KEY, terminate_id); return False
    prc = id_process_map[terminate_id]
    prc.terminate()
    id_process_map.pop(terminate_id)
    return True

def _publish_password_outputs():
    try:
        pwd_file = open(JOHN_OUTPUT_FILE, 'r')
        for line in pwd_file:
            hash, pwd = line.split(':')
            user_id = _get_user_id(hash)
            if user_id is None:
                pwd_file.close()
                raise Exception("User id not found for hash: " + hash)
            
        pwd_file.close()
    except FileNotFoundError as e:
        log_output("_publish_password_outputs: Pwd output file not created for flushing to db", log_level=LOGLEVEL.ERROR)
    except Exception as e:
        log_output("_publish_password_outputs: %s" % repr(e), log_level=LOGLEVEL.ERROR)

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
        is_terminated, is_completed = False, False
        terminate_id = redisClient.lpop(TERMINATE_KEY, timeout=0)
        if terminate_id is not None: is_terminated = _handle_termination(terminate_id); continue
        for user_id in id_process_map:
            if id_process_map[user_id].poll() == 0: is_completed = True; break
        if is_terminated or is_completed: _publish_password_outputs()
                
        
        work = redisClient.lpop(WORK_KEY, timeout=0)
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
