# FROM python:3.9-alpine
FROM alpine:3.14

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools wheel
# RUN apk add --no-cache python3 nodejs py3-pip g++

RUN pip3 install flask Flask-Debug redis jsonpickle requests minio sqlalchemy pymysql

RUN apk add --no-cache nodejs npm

RUN mkdir -p /svr/app
COPY app /svr/app
COPY app.sh /svr

WORKDIR /svr/app/frontend

RUN npm install
RUN npm run build
RUN rm -rf node_modules

WORKDIR /svr

EXPOSE 5000
# WORKDIR /
# CMD   FLASK_APP=app flask run -h 0.0.0.0

ENV FLASK_PORT 5000
CMD [ "/bin/sh", "-x", "/svr/app.sh" ]
