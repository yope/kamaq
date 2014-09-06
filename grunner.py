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
import sys
import signal
import asyncore
from gpio import AsyncGPInput

class GRunner(object):
	def __init__(self, argv):
		self.sc = None
		self.cfg = Config("grunner.conf")
		self.dim = self.cfg.settings["num_motors"]
		self.audiodev = self.cfg.settings["sound_device"]
		cmd = None
		vec = [0.0 for x in range(self.dim)]
		speed = 3600.0 / 60.0
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
			else:
				print "Unknown command-line option:", a
				return
		signal.signal(signal.SIGINT, self.signal_handler)
		if cmd == None:
			return
		elif cmd == "-i":
			print "Executing G-Code file:", fname
			self.run_file(fname)
		elif cmd == "-g":
			print "Executing single movement to:", repr(vec), "at speed:", speed
			self.move_to(vec, speed)
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
		print " -g                : Process one move\n"
		print "Options for command -g:"
		print " -x <num>          : Move to X-coordinate <num> in millimeters (default 0)"
		print " -y <num>          : Y-coordinate"
		print " -z <num>          : Z-coordinate"
		print " -e <num>          : Extruder movement"
		print " -f <speed>        : Feedrate in mm/minute"

	def prepare_endswitches(self):
		self.esw = {}
		for axis in ["X", "Y", "Z"]:
			eswname = "endstop_" + axis
			self.esw[eswname] = AsyncGPInput(eswname, self)

	def gpio_event(self, name):
		gpi = self.esw[name]
		print "GPIO Event from", name, "value:", gpi.read_value()

	def end_of_file(self):
		self.sc.close()
		sys.exit(0)

	def signal_handler(self, signal, frame):
		print('You pressed Ctrl+C!')
		if self.sc is not None:
			self.sc.zero_output()
			self.sc.close()
		sys.exit(0)

	def move_to(self, vec, speed):
		self.prepare_endswitches()
		m = Move(self.cfg, None)
		self.sc = StepperCluster(self.audiodev, self.dim, self.cfg, None)
		self.sc.set_feedrate(speed)
		self.sc.set_destination(m.transform(vec))
		self.scd = StepperClusterDispatcher(self.sc, self)
		asyncore.loop()

	def run_file(self, fname):
		self.prepare_endswitches()
		g = GCode(self.cfg, fname)
		m = Move(self.cfg, g)
		self.sc = StepperCluster(self.audiodev, self.dim, self.cfg, m)
		self.scd = StepperClusterDispatcher(self.sc, self)
		asyncore.loop()

if __name__ == "__main__":
	gr = GRunner(sys.argv[1:])
