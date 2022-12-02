#!/bin/sh

cd /svr

# export FLASK_DEBUG=1
export FLASK_APP=app

echo "Existing directory at " $(pwd)

nohup flask run -h 0.0.0.0 -p $FLASK_PORT
# flask run -h 0.0.0.0 -p $FLASK_PORT
