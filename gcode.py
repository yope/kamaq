#!/usr/bin/env python
#
# vim: set tabstop=4:
#
# Copyright (c) 2014 David Jander
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

from math import *
import sys

class GCode(object):
	def __init__(self, cfg, filename):
		if isinstance(filename, str):
			self.f = open(filename, "r")
		else:
			self.f = filename # Assume it's a file-like object
		self.dim = cfg.settings["num_motors"]
		self.motor_name = cfg.settings["motor_name"]
		self.pos = {}
		for m in self.motor_name:
			self.pos[m] = 0.0
		self.pos["F"] = 0.0 # Feedrate
		self.pos["command"] = "position" # Default position command
		self.commands = self.command_generator()
		self.zero_extruder = False

	def set_zero_extruder(self, val):
		self.zero_extruder = val

	def process_M(self, code, args):
		if code == 82: # Absolute E codes
			pass
		elif code == 104: # Set hotend temperature
			val = float(args[0][1:])
			print("Set temperature:", val, "deg. C")
			return {"command": "setpoint", "type": "hotend", "value": val}
		elif code == 106: # Set extruder fan speed
			print("Set extruder fan speed:", args[0])
		else:
			print("Unimplemented M: code =", code, repr(args))
		return None

	def process_G(self, code, args):
		if code == 1 or code == 0: # Controlled movement
			for code in args:
				val = args[code]
				if code in self.pos:
					if code == "F":
						val = val / 60
					self.pos[code] = val
				else:
					print("G1 unknown code:", code)
			if self.zero_extruder:
				self.pos["E"] = 0.0
			return self.pos
		elif code == 21: # Set metric units
			pass
		elif code == 28: # Home position
			print("Home position")
			return {"command": "home"}
		elif code == 90: # Absolute positioning
			print("Set Home and absolute positioning")
			return {"command": "sethome"}
		elif code == 92: # Set home
			# TODO: Implement home offsetting
			pass
		else:
			print("Unimplemented G: code =", code, repr(args))
		return None

	def process_T(self, code, args):
		if code == 0: # Tool selection 0
			pass
		else:
			print("Unimplemented T: code =", code, repr(args))

	def process_line(self, cmd, l):
		words = l.split()
		try:
			code = int(words[0], 10)
		except ValueError:
			return None
		words = words[1:]
		args = {}
		for w in words:
			if w[0] == ";":
				break
			if w[0] in ["X", "Y", "Z", "E", "F", "S", "P", "R"]:
				snum = w[1:]
				if "." in snum:
					num = float(snum)
				else:
					num = int(snum)
				args[w[0]] = num
		if cmd == "G":
			return self.process_G(code, args)
		elif cmd == "M":
			return self.process_M(code, args)
		elif cmd == "T":
			return self.process_T(code, args)

	def command_generator(self):
		for l in self.f:
			cmd = l[0]
			if cmd == ";":
				print(l.strip(" \r\n"))
			if not cmd in ['G', 'M', 'T']:
				continue
			ret = self.process_line(cmd, l[1:].strip(" \r\n"))
			if ret is not None:
				yield ret
		self.f.close()
		raise StopIteration

if __name__ == "__main__":
	cfg = Config("bla.ini")
	g = GCode(cfg, sys.argv[1])

