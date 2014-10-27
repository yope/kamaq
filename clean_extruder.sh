#!/bin/sh

TEMP=260.0
MOVE=1
SHORT=0

show_help () {
	echo "Command line optios:"
	echo " -t <temp>      : Adjust temperature (default 260.0)"
	echo " -s             : short process"
	echo " -n             : no movements"
}

while getopts "h?snt:" opt; do
    case "$opt" in
    h)
        show_help
        exit 0
        ;;
    n) MOVE=0
        ;;
    t) TEMP=$OPTARG
        ;;
    s) SHORT=1
    esac
done

shift $((OPTIND-1))

if [ $MOVE -eq 1 ]; then
	./grunner.py -g -x 10 -y 10 -z 5 -f 6000
	./grunner.py -H
	./grunner.py -g -x 50 -y 50 -z 30 -f 6000
fi
if [ $SHORT -eq 0 ]; then
	./grunner.py -g -e 0.1 -f 500 -t $TEMP
	./grunner.py -g -e 0.1 -f 500 -t $TEMP
fi
./grunner.py -g -e 0.1 -f 500 -t $TEMP
echo "Turn on FAN"
if [ $SHORT -eq 0 ]; then
	./grunner.py -g -e 5 -f 50 -t $TEMP
	./grunner.py -g -e 5 -f 50 -t $TEMP
fi
./grunner.py -g -e 10 -f 80 -t $TEMP
./grunner.py -g -e 30 -f 120 -t $TEMP

