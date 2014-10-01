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
		self.dim = cfg.settings["num_motors"]
		self.motor_name = cfg.settings["motor_name"]
		self.print_volume = cfg.settings["print_volume"]
		self.motor_name_indexes = {}
		for i in range(len(self.motor_name)):
			self.motor_name_indexes[self.motor_name[i]] = i
		self.gcode = gcode
		if gcode is not None:
			self.start()
		self.feedrate = 0.0
		self.feedrate0 = 0.0

	def start(self):
		self.movements = self.movement_generator()

	def transform(self, gpos):
		ret = map(lambda x, y: x * y, gpos, self.mm2steps)
		return ret

	def _dist(self, vec):
		return sqrt(sum(map(lambda x: x*x, vec)))

	def set_feedrate(self, fr):
		self.feedrate = fr

	def get_feedrate(self):
		return self.feedrate

	def transform_feedrate(self, po, pt):
		sf = (self._dist(pt) / self._dist(po)) / 80.0
		self.feedrate *= sf

	def homing_generator(self):
		pos = {}
		pos["command"] = "position"
		for i in range(3):
			pos = [0] * self.dim
			pos[i] = -self.print_volume[i]
			p = self.transform(pos)
			if i < 2:
				self.set_feedrate(80.0)
			else:
				self.set_feedrate(2.0)
			self.transform_feedrate(pos, p)
			yield ("feedrate", self.feedrate)
			yield ("position", p)
			yield ("sethome", None)
			pos[i] = 4
			p = self.transform(pos)
			yield ("position", p)
			if i < 2:
				self.set_feedrate(5.0)
			else:
				self.set_feedrate(1.0)
			pos[i] = -6
			p = self.transform(pos)
			self.transform_feedrate(pos, p)
			yield ("feedrate", self.feedrate)
			yield ("position", p)
			yield ("sethome", None)

	def movement_generator(self):
		while True:
			try:
				obj = next(self.gcode.commands)
			except StopIteration:
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
						self.set_feedrate(obj[w])
				p = self.transform(pos)
				self.transform_feedrate(pos, p)
				if self.feedrate != self.feedrate0:
					self.feedrate0 = self.feedrate
					yield ("feedrate", self.feedrate)
				yield ("position", p)
			elif cmd == "home":
				homing = self.homing_generator()
				while True:
					try:
						cmd = next(homing)
					except StopIteration:
						break
					yield cmd
			elif cmd == "sethome":
				yield (cmd, None)
			elif cmd == "setpoint":
				pass
		raise StopIteration

