#!/bin/bash
set -e
TIMEOUT=300   #to solve upload app package timeout issue

cd /home/ada/prod/vision/apps

# activate the virtualenv
source /opt/envs/mami/bin/activate

# used for web requests
exec python manage.py run_gunicorn -w 1 \
    --user=mami --group=mami \
    --settings=settings.local \
    --timeout=$TIMEOUT \
    --bind=0.0.0.0:8000 \
    --log-level=info \
    --log-file=/home/mami/prod/mami-server/logs/mami.log 2>>/home/mami/prod/mami-server/logs/mami.log

## following will be used in future.
#exec `python manage.py run_gunicorn -w 1 \
#    --user=mami --group=mami \
#    --settings=settings.local \
#    --bind=0.0.0.0:8000 \
#    --log-level=info \
#    --log-file=/home/mami/prod/mami-server/logs/mami.log 3>>/home/mami/prod/mami-server/logs/mami.log` ; \
#`python manage.py run_gunicorn -w 1 \
#    --user=mami --group=mami \
#    --settings=settings.local_s \
#    --bind=0.0.0.0:8001 \
#    --log-level=info \
#    --log-file=/home/mami/prod/mami-server/logs/mami.log 2>>/home/mami/prod/mami-server/logs/mami.log`

# used for api requests, the sig and client_key are needed for all api requests
