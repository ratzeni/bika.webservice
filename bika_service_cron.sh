#!/bin/bash

. ./init.cfg

nohup python $SERVICE_DIR/bika_service.py --pid-file $PID_FILE --log-file $LOG_FILE --host $HOST --port $PORT

exit
