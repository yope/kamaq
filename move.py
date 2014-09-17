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

from math import *
from gcode import GCode
import signal
import sys

class Move(object):
	def __init__(self, cfg, gcode):
		self.mm2steps = [float(x * (1 - int(y) * 2)) for x, y in zip(
				cfg.settings["steps_per_mm"], cfg.settings["invert_motor"])]
		print repr(self.mm2steps)
		self.dim = cfg.settings["num_motors"]
		self.motor_name = cfg.settings["motor_name"]
		self.print_volume = cfg.settings["print_volume"]
		self.motor_name_indexes = {}
		for i in range(len(self.motor_name)):
			self.motor_name_indexes[self.motor_name[i]] = i
		self.gcode = gcode
		if gcode is not None:
			self.start()
		self.homing = None

	def start(self):
		self.movements = self.movement_generator()

	def transform(self, gpos):
		ret = map(lambda x, y: x * y, gpos, self.mm2steps)
		return ret

	def start_homing(self):
		self.homing = self.homing_generator()

	def homing_generator(self):
		pos = {}
		pos["command"] = "position"
		for i in range(3):
			for m in self.motor_name:
				pos[m] = 0.0
			pos[self.motor_name[i]] = -self.print_volume[i]
			if i < 2:
				pos["F"] = 80.0
			else:
				pos["F"] = 120.0
			yield pos
			yield {"command" : "sethome"}
			if i < 2:
				pos["F"] = 5.0
			else:
				pos["F"] = 60.0
			pos[self.motor_name[i]] = 4
			yield pos
			pos[self.motor_name[i]] = -6
			yield pos
			yield {"command" : "sethome"}
			if i >= 2:
				continue
			pos[self.motor_name[i]] = 4
			yield pos
			pos[self.motor_name[i]] = -6
			yield pos
			yield {"command" : "sethome"}

	def movement_generator(self):
		while True:
			if self.homing:
				gen = self.homing
			else:
				gen = self.gcode.commands
			try:
				obj = next(gen)
			except StopIteration:
				if gen == self.homing:
					self.homing = None
					continue
				else:
					break
			if not "command" in obj:
				print "MOVE: Unknown command object:", repr(obj)
				continue
			cmd = obj["command"]
			if cmd == "position":
				pos = [0] * self.dim
				for w in obj:
					idx = self.motor_name_indexes.get(w, None)
					if idx is not None:
						pos[idx] = obj[w]
					elif w == "F":
						yield ("feedrate", obj[w])
				p = self.transform(pos)
				yield ("position", p)
			elif cmd == "home":
				self.start_homing()
			elif cmd == "sethome":
				yield (cmd, None)
		raise StopIteration

