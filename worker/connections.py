import redis
import minio
import sqlalchemy as db

from config import *

__author__ = "Siddharth Srinivasan"

redisClient = redis.StrictRedis(host=RedisConfig.HOST, port=RedisConfig.PORT, db=0)
minioClient = minio.Minio(f"{MinIOConfig.HOST}:{MinIOConfig.PORT}",
               access_key=MinIOConfig.USER,
               secret_key=MinIOConfig.PWD, secure=False)

class DBEntities(object):
     ENGINE = db.create_engine(f"mysql+pymysql://{MySQLConfig.USER}:{MySQLConfig.PWD}@{MySQLConfig.URI}/{MySQLConfig.DB}")
     CONNECTION = ENGINE.connect()
     META = db.MetaData()

     USER_TABLE = db.Table(
        'user_inputs', META,
        db.Column('userId', db.String, primary_key=True, nullable=False),
        db.Column('crackingMode', db.String, nullable=False),
        db.Column('hashFile', db.String, nullable=False),
        db.Column('wordlistFile', db.String),
        db.Column('hashType', db.String, server_default='crypt'),
        db.Column('status', db.String, server_default='pending')
    )

     PASSWORD_TABLE = db.Table(
        'password_outputs', META,
        db.Column('userId', db.String, primary_key=True, nullable=False),
        db.Column('hash', db.String, primary_key=True, nullable=False),
        db.Column('password', db.String, nullable=False),
        db.Column('hash_type', db.String, primary_key=True, nullable=False),
        db.Column('salt', db.String)
    )