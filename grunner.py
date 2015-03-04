#!/usr/bin/env python3
#
# vim: set tabstop=4:
#
# Copyright (c) 2014 David Jander
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import monkeypatch
from config import Config
from gcode import GCode
from stepper import StepperCluster
from move import Move
from config import Config
from printer import Printer
from webui import WebUi
import sys
import signal
import asyncio
import time
from io import StringIO

class GRunner(object):
	def __init__(self, argv):
		self.sc = None
		self.cfg = Config("kamaq.conf")
		self.dim = self.cfg.settings["num_motors"]
		self.audiodev = self.cfg.settings["sound_device"]
		cmd = None
		vec = [0.0 for x in range(self.dim)]
		speed = 3600.0
		self.limit = None
		self.speed_scale = 1.0
		self.temp = None
		self.btemp = None
		self.pid = {}
		self.zero_extruder = False
		self.webui = None
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
				speed = float(argv.pop(0))
			elif a == "-h" or a == "--help":
				self.print_help()
				return
			elif a == "-s":
				self.speed_scale = float(argv.pop(0))
			elif a == "-t":
				self.temp = float(argv.pop(0))
			elif a == "-b":
				self.btemp = float(argv.pop(0))
			elif a == "-l":
				self.limit = float(argv.pop(0)) / 60.0
			elif a == "-w":
				#self.webui = WebUi(self.printer)
				#self.printer.add_webui(self.webui)
				self.run_webui()
			elif a == "--no-extrusion":
				self.zero_extruder = True
			else:
				print("Unknown command-line option:", a)
				return
		signal.signal(signal.SIGINT, self.signal_handler)
		self.loop = asyncio.get_event_loop()
		if cmd == None:
			return
		elif cmd == "-i":
			print("Executing G-Code file:", fname)
			self.run_file(fname)
		elif cmd == "-g":
			print("Executing single movement to:", repr(vec), "at speed:", speed)
			self.move_to(vec, speed)
		elif cmd == "-H":
			self.homing()
		else:
			print("Error: Unimplemented command:", cmd)
			return
		self.loop.run_forever()

	def print_help(self):
		name = sys.argv[0]
		print("%s: G-Code runner" % (name))
		print("Syntax:")
		print("   %s [-i <filename>|-g|-H] [options]\n" % (name))
		print("Commands:")
		print(" -i <filename>     : Execute all G-codes from file <filename>")
		print(" -g                : Process one move")
		print(" -H                : Home position")
		print("\nCommon options:")
		print(" -t <temp>         : Set extruder temperature")
		print(" -b <temp>         : Set heated bed temperature")
		print(" -w                : Launch web interface")
		print("\nOptions for command -g:")
		print(" -x <num>          : Move to X-coordinate <num> in millimeters (default 0)")
		print(" -y <num>          : Y-coordinate")
		print(" -z <num>          : Z-coordinate")
		print(" -e <num>          : Extruder movement")
		print(" -f <speed>        : Feedrate in mm/minute")
		print("\nOptions for command -i:")
		print(" -s <factor>       : Speed scale factor (default 1.0)")
		print(" -l <limit>        : Set feedrate limit")
		print(" --no-extrusion    : Do not move extruder")

	def end_of_file(self):
		print("EOF")
		if not self.webui:
			self.shutdown()

	def shutdown(self):
		self.printer.shutdown()
		if self.sc is not None:
			self.sc.zero_output()
			self.sc.zero_output()
			self.sc.zero_output()
			self.sc.zero_output()
			self.sc.close()
		sys.exit(0)

	def run_webui(self):
		signal.signal(signal.SIGINT, self.signal_handler)
		self.loop = asyncio.get_event_loop()
		sc = StepperCluster(self.audiodev, self.dim, self.cfg)
		self.printer = Printer(self.cfg, sc)
		self.webui = WebUi(self.printer)
		self.printer.add_webui(self.webui)
		self.printer.run()

	def signal_handler(self, signal, frame):
		print('You pressed Ctrl+C!')
		self.shutdown()

	def preheat(self):
		if not self.temp and not self.btemp:
			return
		pids = []
		if self.temp:
			pids.append(("ext", self.temp))
		if self.btemp:
			pids.append(("bed", self.btemp))
		for name, sp in pids:
			self.printer.launch_pid(name, sp)
		while True:
			leave = True
			for name, sp in pids:
				tmp = self.printer.get_temperature(name)
				if tmp < (sp - 3.0):
					leave = False
				print(name+": temp =", tmp, "sp =", sp, end=' ')
			print("")
			self.loop.run_until_complete(asyncio.sleep(1))
			if leave:
				break
		# Add some delay here to ensure good heat distribution/melting
		print("Setpoint reached.")
		for i in range(30):
			for name, sp in pids:
				tmp = self.printer.get_temperature(name)
				print(name+": temp =", tmp, "sp =", sp, end=' ')
			print("")
			self.loop.run_until_complete(asyncio.sleep(1))

	def move_to(self, vec, speed):
		print("Currently not supported. Use the web interface!")
		return
		cmd = "G1 "
		for v, n in zip(vec, ["X", "Y", "Z", "E"]):
			cmd += n + str(v) + " "
		cmd += "F" + str(speed) + " "
		f = StringIO(cmd + "\n")
		self.run_file(f)

	def run_file(self, fname):
		print("Currently not supported. Use the web interface!")
		return
		g = GCode(self.cfg, fname)
		g.set_zero_extruder(self.zero_extruder)
		m = Move(self.cfg, g, self.printer)
		self.preheat()
		self.sc = StepperCluster(self.audiodev, self.dim, self.cfg, m)
		self.sc.set_speed_scale(self.speed_scale)
		self.sc.set_max_feedrate(self.limit)
		self.scd = StepperClusterDispatcher(self.sc, self)

	def homing(self):
		f = StringIO("G28\n")
		self.run_file(f)

if __name__ == "__main__":
	gr = GRunner(sys.argv[1:])
