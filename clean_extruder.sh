#!/bin/sh

if [ -z "$1" ]; then
	TEMP=260.0
else
	TEMP=$1
fi

./grunner.py -g -x 10 -y 10 -z 5 -f 6000
./grunner.py -H
./grunner.py -g -x 50 -y 50 -z 30 -f 6000
./grunner.py -g -e 0.1 -f 500 -t $TEMP
./grunner.py -g -e 0.1 -f 500 -t $TEMP
./grunner.py -g -e 0.1 -f 500 -t $TEMP
./grunner.py -g -e 0.1 -f 500 -t $TEMP
echo "Turn on FAN"
./grunner.py -g -e 5 -f 200 -t $TEMP
./grunner.py -g -e 5 -f 200 -t $TEMP
./grunner.py -g -e 5 -f 200 -t $TEMP
./grunner.py -g -e 20 -f 400 -t $TEMP

