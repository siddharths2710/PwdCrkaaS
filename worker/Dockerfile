FROM python:3.9

USER root

#ENV TORCH_HOME=/data/models

# Install Git
RUN apt update && apt install john -y


RUN mkdir /app
RUN python3 -m pip install redis minio sqlalchemy pymysql
COPY config.py worker.py connections.py /app/
WORKDIR /app

#CMD [ "python3", "worker.py"]