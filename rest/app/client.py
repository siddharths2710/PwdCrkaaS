from app import app
import redis
from minio import Minio

inputBucket = app.config['INPUT_BUCKET']
wordlistBucket = app.config['WORDLIST_BUCKET']

redisClient = redis.Redis(
    host=app.config['REDIS_SERVICE_HOST'], port=app.config['REDIS_SERVICE_PORT'])

minioHost = "%s:%s" % (
    app.config['MINIO_SERVICE_HOST'], app.config['MINIO_SERVICE_PORT'])
minioClient = Minio(minioHost,
                    secure=False,
                    access_key=app.config['MINIO_SERVICE_USER'],
                    secret_key=app.config['MINIO_SERVICE_PASS'])

try:
    if not minioClient.bucket_exists(inputBucket):
        minioClient.make_bucket(inputBucket)
except Exception as e:
    app.logger.error("Error making the hashbucket bucket", exc_info=e)

try:
    if not minioClient.bucket_exists(wordlistBucket):
        minioClient.make_bucket(wordlistBucket)
except Exception as e:
    app.logger.error("Error making the wordlist bucket", exc_info=e)

