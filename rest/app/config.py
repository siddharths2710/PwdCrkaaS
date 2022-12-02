import os

class Config(object):
    REDIS_SERVICE_HOST = os.environ.get('REDIS_SERVICE_HOST') or 'localhost'
    REDIS_SERVICE_PORT = os.environ.get('REDIS_SERVICE_PORT') or 6379

    MINIO_SERVICE_HOST = os.environ.get('MINIO_SERVICE_HOST') or 'localhost'
    MINIO_SERVICE_PORT = os.environ.get('MINIO_SERVICE_PORT') or 9000
    MINIO_SERVICE_USER = os.environ.get('MINIO_SERVICE_USER') or "rootuser"
    MINIO_SERVICE_PASS = os.environ.get('MINIO_SERVICE_PASS') or "rootpass123"

    # QUEUE_BUCKET = os.environ.get('QUEUE_BUCKET') or "queue"
    # OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET') or "output"

    INPUT_BUCKET = os.environ.get('INPUT_BUCKET') or 'input-bucket'
    WORDLIST_BUCKET = os.environ.get('WORDLIST_BUCKET') or 'wordlist-bucket'

    MYSQL_DB = os.environ.get('MYSQL_DB') or 'local_db'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = os.environ.get('MYSQL_PORT') or '3306'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PWD = os.environ.get('MYSQL_PWD') or 'pwned'

    WORK_KEY = "toWorker"
    TERMINATE_KEY = "toTerminate"

