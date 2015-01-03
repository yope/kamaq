#!/bin/sh

TEMP=260.0
MOVE=1
SHORT=0

show_help () {
	echo "Command line optios:"
	echo " -b <temp>      : Adjust bed temperature (default none)"
	echo " -t <temp>      : Adjust temperature (default 260.0)"
	echo " -s             : short process"
	echo " -n             : no movements"
}
BED=""
while getopts "h?snt:b:" opt; do
    case "$opt" in
    h)
        show_help
        exit 0
        ;;
    n)
	MOVE=0
        ;;
    t)
	TEMP=$OPTARG
        ;;
    b)
	BED="-b $OPTARG"
	;;
    s)
	SHORT=1
	;;
    esac
done

shift $((OPTIND-1))

if [ $MOVE -eq 1 ]; then
	./grunner.py -H
	./grunner.py -g -x 50 -y 50 -z 30 -f 5000
fi
if [ $SHORT -eq 0 ]; then
	./grunner.py -g -e 0.1 -f 500 -t $TEMP $BED
	./grunner.py -g -e 0.1 -f 500 -t $TEMP $BED
fi
./grunner.py -g -e 0.1 -f 500 -t $TEMP $BED
echo "Turn on FAN"
if [ $SHORT -eq 0 ]; then
	./grunner.py -g -e 5 -f 50 -t $TEMP $BED
	./grunner.py -g -e 5 -f 50 -t $TEMP $BED
fi
./grunner.py -g -e 10 -f 80 -t $TEMP $BED
./grunner.py -g -e 30 -f 120 -t $TEMP $BED

