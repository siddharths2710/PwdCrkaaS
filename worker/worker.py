#! /usr/bin/env python3

import os
import sys
import time
import shutil
import tempfile
import subprocess
import minio.error
import sqlalchemy as db

from config import *
from connections import *

__author__ = "Siddharth Srinivasan"


# https://stackoverflow.com/questions/33053241/sqlalchemy-if-table-does-not-exist


# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_creating_table.htm
# https://towardsdatascience.com/sqlalchemy-python-tutorial-79a577141a91

id_hash_map = {}
id_process_map = {}
pwd_insert_query = db.insert(DBEntities.PASSWORD_TABLE)

def _get_user_id(pwd_hash):
    for user_id in id_hash_map:
        if pwd_hash in id_hash_map[user_id]:
            return user_id
    return None

def _handle_termination(terminate_id):
    if terminate_id not in id_process_map: redisClient.lpush(RedisConfig.TERMINATE_KEY, terminate_id); return False
    prc = id_process_map[terminate_id]
    prc.terminate()
    time.sleep(5)
    id_process_map.pop(terminate_id)
    return True

def _publish_password_outputs(user_id):
    try:
        pwd_file = open(JohnConfig.OUTPUT_FILE, 'r')
        outputs_list = []
        for line in pwd_file:
            hash, pwd = line.split(':')
            if user_id is None: user_id = _get_user_id(hash)
            if user_id is None:
                pwd_file.close()
                raise Exception("User id not found for hash: " + hash)
            outputs_list.append({
                'userId': user_id, 'hash': hash, 'password': pwd, 'hash_type': 'crypt'
            })
        with DBEntities.CONNECTION.begin():
            result_proxy = DBEntities.CONNECTION.execute(pwd_insert_query, outputs_list)
        pwd_file.close()
        os.remove(JohnConfig.OUTPUT_FILE)
        id_process_map.pop(user_id, None)
    except FileNotFoundError as e:
        log_output("_publish_password_outputs: Pwd output file not created for flushing to db", log_level=LOGLEVEL.ERROR)
    except Exception as e:
        log_output("_publish_password_outputs: %s" % repr(e), log_level=LOGLEVEL.ERROR)

def log_output(message, key=LogConfig.KEY, log_level=LogConfig.LEVEL):
    print("Worker", log_level.name, ":", message, file=sys.stdout)
    redisClient.lpush('logging', f"Worker:{log_level.name}:{key}:{message}")

log_output("Started Worker pod")

try:
    if not DBEntities.ENGINE.dialect.has_table(DBEntities.CONNECTION, DBEntities.PASSWORD_TABLE): 
        DBEntities.META.create_all(DBEntities.ENGINE)
    while not DBEntities.ENGINE.dialect.has_table(DBEntities.CONNECTION, DBEntities.USER_TABLE): 
        log_output("User_Inputs db still to be created")
    while not minioClient.bucket_exists(MinIOConfig.WORDLIST_BUCKET):
                log_output(f"{MinIOConfig.WORDLIST_BUCKET}: Not created")
                time.sleep(1000)
                continue
except minio.error.S3Error as e: log_output(f"{MinIOConfig.WORDLIST_BUCKET} creation error: " + repr(e), log_level=LOGLEVEL.ERROR)
except minio.error.InvalidResponseError as e: log_output("MinIO API Error: " + repr(e), log_level=LOGLEVEL.ERROR)
except Exception as e: log_output("Error: " + repr(e), log_level=LOGLEVEL.ERROR)

while True:
        is_terminated, is_completed = False, False
        terminate_id = redisClient.lpop(RedisConfig.TERMINATE_KEY)
        if terminate_id is not None: 
            is_terminated = _handle_termination(terminate_id); 
            log_output("is_terminated: " + str(is_terminated))
            continue
        for user_id in id_process_map:
            if id_process_map[user_id].poll() == 0: 
                status_update_query = db.update(DBEntities.USER_TABLE) \
                .where(DBEntities.USER_TABLE.c.userId == user_id).values(status='done')
                with DBEntities.CONNECTION.begin():
                    result_proxy = DBEntities.CONNECTION.execute(status_update_query)
                    log_output("is_completed setting to True")
                    is_completed = True; 
                break
        if is_terminated or is_completed: _publish_password_outputs(user_id); continue
                
        
        work = redisClient.lpop(RedisConfig.WORK_KEY)
        if work is None: continue
        user_id = work.decode('utf-8')
        log_output(f"Received cracking request from user: {user_id}")
        try:
            input_query = DBEntities.USER_TABLE.select().where(DBEntities.USER_TABLE.c.userId == user_id)
            query_output = DBEntities.CONNECTION.execute(input_query)
            _, crackingMode, hashFile, wordlistFile, hashType, status = query_output.fetchone()
            
            dir_path = tempfile.mkdtemp()
            input_path = os.path.join(dir_path, f"{user_id}.txt")
            minioClient.fget_object(MinIOConfig.INPUT_BUCKET, user_id, input_path)
            
            log_output("Running password cracking utility")
            
            cmd_params = ["/usr/sbin/john"]
            if crackingMode == "wordlist":
                wordlist_path = os.path.join(dir_path, "wordlist.txt")
                minioClient.fget_object(MinIOConfig.WORDLIST_BUCKET, wordlistFile, wordlist_path)
                cmd_params.append(f"--wordlist:{wordlist_path}")
            elif crackingMode is not None:
                cmd_params.append(f"--{crackingMode}")

            if hashType is None or hashType == 'crypt':
                cmd_params.append("--format=crypt")
            else:
                cmd_params.append(f"--format={hashType}")

            cmd_params.append(input_path)
            
            status_update_query = db.update(DBEntities.USER_TABLE) \
            .where(DBEntities.USER_TABLE.c.userId == user_id).values(status='progress')
            result_proxy = DBEntities.CONNECTION.execute(status_update_query)
            result = subprocess.Popen(cmd_params)
            id_process_map[user_id] = result
        except minio.error.S3Error as e: log_output("MinIO Bucket/File Operation Failure: " + repr(e), log_level=LOGLEVEL.ERROR)
        except minio.error.InvalidResponseError as e: log_output("MinIO API Error: " + repr(e), log_level=LOGLEVEL.ERROR)
        except Exception as e: log_output("Error: " + repr(e), log_level=LOGLEVEL.ERROR)
