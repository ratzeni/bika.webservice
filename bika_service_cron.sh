#!/bin/bash

# This script can be used to handle the galaxy_menus service as a cronjob
# add to the crontab a line like
#
# */5 * * * * $BIOBANK_REPO_PATH/services/galaxy_menus_service_cron.sh &

SERVICE_DIR=/Users/utente/PycharmProjects/bika/bika.webservice
PID_FILE=~/tmp/bika_service.pid
HOST=0.0.0.0
PORT=8088

nohup python $SERVICE_DIR/bika_service.py --pid-file $PID_FILE --host $HOST --port $PORT
