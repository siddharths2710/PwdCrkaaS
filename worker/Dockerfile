FROM python:3.8

USER root
ENV TORCH_HOME=/data/models

# Install Git
RUN apt install git

# Install Facebook Demucs
RUN mkdir -p /lib/demucs

WORKDIR /lib/demucs

RUN git clone -b main --single-branch https://github.com/facebookresearch/demucs /lib/demucs

RUN python3 -m pip install -e .

RUN apt update
RUN apt install -y git ffmpeg

RUN python3 -m demucs.separate -d cpu test.mp3 # Trigger model download
RUN rm -r separated  # cleanup

VOLUME /data/input
VOLUME /data/output
VOLUME /data/models

RUN mkdir /app
RUN python3 -m pip install redis minio
COPY worker.py /app/
WORKDIR /app

CMD [ "python3", "worker.py"]