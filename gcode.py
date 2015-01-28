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
	def __init__(self, cfg):
		self.dim = cfg.settings["num_motors"]
		self.motor_name = cfg.settings["motor_name"]
		self.pos = {}
		for m in self.motor_name:
			self.pos[m] = 0.0
		self.pos["F"] = 0.0 # Feedrate
		self.pos["command"] = "position" # Default position command
		self.set_zero_extruder(False)
		self.relative_mode = False

	def set_zero_extruder(self, val):
		self.zero_extruder = val

	def process_M(self, code, args):
		if code == 82: # Absolute E codes
			pass
		elif code == 104: # Set hotend temperature
			val = float(args['S'])
			print("Set temperature:", val, "deg. C")
			return {"command": "setpoint", "type": "hotend", "value": val}
		elif code == 106: # Set extruder fan speed
			print("Set extruder fan speed:", args.get("S", 0))
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
					if self.relative_mode and code in ['X', 'Y', 'Z', 'E']:
						self.pos[code] += val
					else:
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
			ret = {"command": "home"}
			ret.update(args)
			return ret
		elif code == 90: # Absolute positioning
			print("Set absolute positioning")
			self.relative_mode = False
		elif code == 91: # Relative positioning
			print("Set relative positioning")
			self.relative_mode = True
		elif code == 92: # Set home
			ret = {"command": "sethome"}
			ret.update(args)
			return ret
		else:
			print("Unimplemented G: code =", code, repr(args))
		return None

	def process_T(self, code, args):
		if code == 0: # Tool selection 0
			pass
		else:
			print("Unimplemented T: code =", code, repr(args))

	def process_line(self, l):
		l = l.strip(" \r\n")
		if len(l) < 2:
			return None
		cmd = l[0]
		words = l[1:].split()
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
				try:
					if "." in snum:
						num = float(snum)
					else:
						num = int(snum)
				except ValueError:
					num = w
				args[w[0]] = num
		if cmd == "G":
			return self.process_G(code, args)
		elif cmd == "M":
			return self.process_M(code, args)
		elif cmd == "T":
			return self.process_T(code, args)
		return None
