#!/bin/sh

./grunner.py -g -x 10 -y 10 -z 1 -f 1000
./grunner.py -H
echo "Adjust screw height and press ENTER"
read a
./grunner.py -g -z 2 -x 85 -f 1000
./grunner.py -g -x 80
./grunner.py -g -z -2 -f 80
echo "Adjust screw height and press ENTER"
read a
./grunner.py -g -z 2 -y 85 -f 1000
./grunner.py -g -y 80
./grunner.py -g -z -2 -f 80
echo "Adjust screw height and press ENTER"
read a
./grunner.py -g -z 2 -x -85 -f 1000
./grunner.py -g -x -80
./grunner.py -g -z -2 -f 80
echo "Adjust screw height and press ENTER"
read a
./grunner.py -g -x 10 -y 10 -z 1 -f 1000
./grunner.py -H

