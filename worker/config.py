import os
import platform
from enum import Enum

__author__ = "Siddharth Srinivasan"

class LOGLEVEL(Enum):
    INFO = 0
    DEBUG = 1
    ERROR = 2

class LogConfig(object):
    KEY = "{}.worker.info".format(platform.node())
    LEVEL = LOGLEVEL.INFO

class JohnConfig(object):
    LOG_FILE = os.path.join(os.path.expanduser('~'), '.john/john.log')
    REC_FILE = os.path.join(os.path.expanduser('~'), '.john/john.rec')
    OUTPUT_FILE = os.path.join(os.path.expanduser('~'), '.john/john.pot')

class RedisConfig(object):
    WORK_KEY = "toWorker"
    TERMINATE_KEY = 'toTerminate'
    HOST = os.getenv("REDIS_HOST") or "localhost"
    PORT = int(os.getenv("REDIS_PORT") or "6379")

class MinIOConfig(object):
    HOST = os.getenv("MINIO_HOST") or "localhost" 
    PORT = int(os.getenv("MINIO_PORT") or "9000")
    
    USER = os.getenv('MINIO_USER') or "rootuser" 
    PWD = os.getenv('MINIO_PWD') or "rootpass123"
    
    INPUT_BUCKET = os.getenv('INPUT_BUCKET') or 'input-bucket'
    WORDLIST_BUCKET = os.getenv('WORDLIST_BUCKET') or 'wordlist-bucket'

class MySQLConfig(object):
    DB = os.getenv('MYSQL_DB') or 'foo'
    URI = os.getenv('MYSQL_URI') or 'localhost'
    USER = os.getenv('MYSQL_USER') or 'scott'
    PWD = os.getenv('MYSQL_PWD') or 'tiger'