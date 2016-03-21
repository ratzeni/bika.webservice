#!/bin/bash

. ./init.cfg

if [[ $1 == "start" || $1 == "stop"  || $1 == "restart" ]]
	then
		nohup python $SERVICE_DIR/bika_service.py --pid-file $PID_FILE --log-file $LOG_FILE --host $HOST --port $PORT --$1
else
	echo "usage: $0 start|stop|restart"
	exit
fi

exit
