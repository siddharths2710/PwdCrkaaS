import os
from flask import Flask
from app.config import Config
# from flask_debug import Debug
import logging

template_dir = os.path.abspath('app/frontend/dist')
static_dir = os.path.abspath('app/frontend/dist')
print(template_dir)
app = Flask(__name__, static_url_path='',
            static_folder=static_dir, template_folder=template_dir)

app.config.from_object(Config)

from app.logger import RedisHandler, formatter

redisHandler = RedisHandler()
redisHandler.setFormatter(formatter)
redisHandler.setLevel(level=logging.INFO)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(redisHandler)

from app import routes
