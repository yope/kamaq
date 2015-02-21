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
from gcode import GCode
import signal
import sys
import asyncio

class Move(object):
	def __init__(self, cfg, printer):
		self.mm2steps = [float(x * (1 - int(y) * 2)) for x, y in zip(
				cfg.settings["steps_per_mm"], cfg.settings["invert_motor"])]
		self.dim = cfg.settings["num_motors"]
		self.motor_name = cfg.settings["motor_name"]
		self.print_volume = cfg.settings["print_volume"]
		self.motor_name_indexes = {}
		for i in range(len(self.motor_name)):
			self.motor_name_indexes[self.motor_name[i]] = i
		self.printer = printer
		self.reset()

	def reset(self):
		self.feedrate = 0.0
		self.feedrate0 = 0.0
		self.orig_feedrate = 0.0
		self.last_pos = [0.0] * self.dim
		self.last_mpos = [0.0] * self.dim

	def transform(self, gpos):
		ret = list(map(lambda x, y: x * y, gpos, self.mm2steps))
		return ret

	def reverse_transform(self, scpos):
		ret = list(map(lambda x, y: x / y, scpos, self.mm2steps))
		return ret

	def _dist(self, vec):
		return sqrt(sum([x*x for x in vec]))

	def _sub(self, vec1, vec2):
		return list(map(lambda x, y: x - y, vec1, vec2))

	def set_feedrate(self, fr):
		self.feedrate = fr
		self.orig_feedrate = fr

	def get_feedrate(self):
		return self.feedrate

	def transform_feedrate(self, po, pt):
		dpo = self._dist(po)
		if dpo:
			sf = (self._dist(pt) / dpo) / 80.0
		else:
			sf = 1.0
		self.feedrate = sf * self.orig_feedrate

	def homing_generator(self, axes):
		pos = {}
		pos["command"] = "position"
		for i in axes:
			pos = [0] * self.dim
			pos[i] = -self.print_volume[i]
			p = self.transform(pos)
			if i < 2:
				self.set_feedrate(50.0)
			else:
				self.set_feedrate(1.5)
			self.transform_feedrate(pos, p)
			yield ("feedrate", self.feedrate)
			yield ("position", p)
			yield ("sethome", None)
			if i < 2:
				pos[i] = 4
			else:
				pos[i] = 2
			p = self.transform(pos)
			yield ("position", p)
			if i < 2:
				self.set_feedrate(4.0)
			else:
				self.set_feedrate(1.0)
			pos[i] = -6
			p = self.transform(pos)
			self.transform_feedrate(pos, p)
			yield ("feedrate", self.feedrate)
			yield ("position", p)
			yield ("sethome", None)

	@asyncio.coroutine
	def process_command(self, obj, queue):
		cmd = obj["command"]
		if cmd == "position":
			pos = [0] * self.dim
			for w in obj:
				idx = self.motor_name_indexes.get(w, None)
				if idx is not None:
					pos[idx] = obj[w]
				elif w == "F":
					self.set_feedrate(obj[w])
			self.printer.set_position_mm(*pos)
			p = self.transform(pos)
			self.transform_feedrate(self._sub(pos, self.last_pos), self._sub(p, self.last_mpos))
			if self.feedrate != self.feedrate0:
				self.feedrate0 = self.feedrate
				yield from queue.put(("feedrate", self.feedrate))
			yield from queue.put(("position", p))
			self.last_pos = pos
			self.last_mpos = p
		elif cmd == "home":
			axes = []
			for w in obj:
				idx = self.motor_name_indexes.get(w, None)
				if idx is not None:
					axes.append(idx)
			if not axes:
				axes = range(3)
			else:
				axes.sort()
			homing = self.homing_generator(axes)
			while True:
				try:
					cmd = next(homing)
				except StopIteration:
					break
				yield from queue.put(cmd)
		elif cmd == "setpoint":
			pass

