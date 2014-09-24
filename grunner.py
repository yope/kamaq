#!/usr/bin/env python
#
# Copyright (c) 2014 David Jander
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# vim: set tabstop=4:

from config import Config
from gcode import GCode
from stepper import StepperCluster, StepperClusterDispatcher
from move import Move
from temp100k import Thermistor100k
from hwmon import ScaledSensor
from config import Config
from gpio import GPOutput
from pid import PidController
import sys
import signal
import asyncore
import time
from cStringIO import StringIO

class GRunner(object):
	def __init__(self, argv):
		self.sc = None
		self.cfg = Config("grunner.conf")
		self.dim = self.cfg.settings["num_motors"]
		self.audiodev = self.cfg.settings["sound_device"]
		cmd = None
		vec = [0.0 for x in range(self.dim)]
		speed = 3600.0 / 60.0
		speed_scale = 1.0
		temp = None
		self.ext_pid = None
		while True:
			try:
				a = argv.pop(0)
			except IndexError:
				break
			if a == "-i":
				fname = argv.pop(0)
				cmd = a
			elif a == "-g":
				cmd = a
			elif a == "-H":
				cmd = a
			elif a == "-x":
				vec[0] = float(argv.pop(0))
			elif a == "-y":
				vec[1] = float(argv.pop(0))
			elif a == "-z":
				vec[2] = float(argv.pop(0))
			elif a == "-e":
				vec[3] = float(argv.pop(0))
			elif a == "-f":
				speed = float(argv.pop(0)) / 60.0
			elif a == "-h" or a == "--help":
				self.print_help()
				return
			elif a == "-s":
				speed_scale = float(argv.pop(0))
			elif a == "-t":
				temp = float(argv.pop(0))
			else:
				print "Unknown command-line option:", a
				return
		signal.signal(signal.SIGINT, self.signal_handler)
		if cmd == None:
			return
		elif cmd == "-i":
			print "Executing G-Code file:", fname
			self.run_file(fname, speed_scale, temp)
		elif cmd == "-g":
			print "Executing single movement to:", repr(vec), "at speed:", speed
			self.move_to(vec, speed)
		elif cmd == "-H":
			self.homing(speed_scale)
		else:
			print "Error: Unimplemented command:", cmd
		return

	def print_help(self):
		name = sys.argv[0]
		print "%s: G-Code runner" % (name)
		print "Syntax:"
		print "   %s [-i <filename>|-g] [options]\n" % (name)
		print "Commands:"
		print " -i <filename>     : Execute all G-codes from file <filename>"
		print " -g                : Process one move"
		print " -H                : Home position"
		print "\nOptions for command -g:"
		print " -x <num>          : Move to X-coordinate <num> in millimeters (default 0)"
		print " -y <num>          : Y-coordinate"
		print " -z <num>          : Z-coordinate"
		print " -e <num>          : Extruder movement"
		print " -f <speed>        : Feedrate in mm/minute"
		print " -t <temp>         : Set extruder temperature"
		print "\nOptions for command -i:"
		print " -s                : Speed scale factor (default 1.0)"

	def end_of_file(self):
		print "EOF"
		self.sc.zero_output()
		self.sc.zero_output()
		self.sc.zero_output()
		self.sc.zero_output()
		self.sc.zero_output()
		self.sc.close()
		sys.exit(0)

	def signal_handler(self, signal, frame):
		print('You pressed Ctrl+C!')
		if self.sc is not None:
			self.sc.zero_output()
			self.sc.close()
			if self.ext_pid:
				self.ext_pid.shutdown()
		sys.exit(0)

	def move_to(self, vec, speed):
		m = Move(self.cfg, None)
		self.sc = StepperCluster(self.audiodev, self.dim, self.cfg, None)
		self.sc.set_feedrate(speed)
		self.sc.set_destination(m.transform(vec))
		self.scd = StepperClusterDispatcher(self.sc, self)
		asyncore.loop()

	def run_file(self, fname, ss, temp=None):
		g = GCode(self.cfg, fname)
		m = Move(self.cfg, g)
		if temp:
			s = ScaledSensor(Config("grunner.conf"), "EXT")
			t = Thermistor100k(s)
			o = GPOutput("heater_EXT")
			self.ext_pid = PidController(t, o, 0.2, 0.002, 0.5)
			self.ext_pid.spawn()
			sp = temp
			self.ext_pid.set_setpoint(sp)
			mtemp = t.read()
			while mtemp < (sp - 5.0):
				mtemp = t.read()
				print "Temp =", mtemp, "setpoint =", sp, "Ouput =", self.ext_pid.get_output()
				time.sleep(1.0)
		self.sc = StepperCluster(self.audiodev, self.dim, self.cfg, m)
		self.sc.set_speed_scale(ss)
		self.scd = StepperClusterDispatcher(self.sc, self)
		asyncore.loop()

	def homing(self, ss):
		f = StringIO("G28\n")
		self.run_file(f, ss)

if __name__ == "__main__":
	gr = GRunner(sys.argv[1:])
