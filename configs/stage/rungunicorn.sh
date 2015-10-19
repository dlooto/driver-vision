#!/bin/bash
set -e
TIMEOUT=300   #to solve upload app package timeout issue

cd /home/ada/prod/vision/apps

# activate the virtualenv
source /opt/envs/nian/bin/activate

# used for web requests
exec python manage.py run_gunicorn -w 1 \
    --user=ada --group=ada \
    --settings=settings.local \
    --timeout=$TIMEOUT \
    --bind=0.0.0.0:8000 \
    --log-level=info \
    --log-file=/home/ada/prod/vision/logs/vision.log 2>>/home/ada/prod/vision/logs/vision.log
