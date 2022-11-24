#!/usr/bin/env python3

import base64
import hashlib
import io

import jsonpickle
from app import app
# from app.client import minioClient, redisClient
# from app.db import db_connection
from flask import make_response, request, send_file, render_template
from flask.wrappers import Response

import minio

__version__ = "api/v1"


@app.route(f"/{__version__}/crack", methods=['POST'])
def crack():
    return "Cracking.."


@app.route(f"/{__version__}/wordlist", methods=['GET'])
def list_wordlist():
    return "[wordlist]"


@app.route("/*")
def hello():
    return render_template('index.html', name='abc')
