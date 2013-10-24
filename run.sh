#!/bin/bash

catched_signal() {
  printf "\rSIGINT caught \n"
  printf "Killed Process $1 \n"
  kill -INT $1
  printf "Killed Process $2 \n"
  kill -INT $2
  sleep 1
}
# Trap the signal Interrupt
trap 'catched_signal $CMD_PID $RCV_PID' SIGINT

./command.py &
CMD_PID=$!
#CMD_PID=1000
./receive-file.py &
RCV_PID=$!
#RCV_PID=1200

tail -n0 -f -
