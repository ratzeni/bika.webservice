#!/bin/bash

. ./init.cfg

nohup python $SERVICE_DIR/bika_service.py --pid-file $PID_FILE_WRITE --log-file $LOG_FILE_WRITE --host $HOST --port $PORT_WRITE --server $SERVER_WRITE &
nohup python $SERVICE_DIR/bika_service.py --pid-file $PID_FILE_READ --log-file $LOG_FILE_READ --host $HOST --port $PORT_READ --server $SERVER_READ &


exit
