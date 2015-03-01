#!/usr/bin/env python
#
# vim: set tabstop=4:
#
# Copyright (c) 2015 David Jander
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

from math import *
import queue

class Interpolator(object):
	def __init__(self, cfg):
		self.max_begin = 12 # FIXME
		self.feedrate0 = None
		self.feedrate1 = None
		self.start = 0
		self.high = 0
		self.end = 0
		self.outq = queue.Queue()
		self.reset()

	def reset(self):
		self.pos0 = [0, 0, 0, 0]
		self.pos1 = None
		self.norm0 = None
		self.last_fr3 = None
		self.obj0 = None

	def _dist(self, vec):
		return sqrt(sum([x*x for x in vec]))

	def _sub(self, vec1, vec2):
		return list(map(lambda x, y: x - y, vec1, vec2))

	def _norm(self, vec):
		d = self._dist(vec)
		if d == 0:
			d = 1.0 # We cannot normalize a vector of zero length...
		return [x / d for x in vec]

	def _dot(self, vec1, vec2):
		return sum(map(lambda a, b: a * b, vec1, vec2))

	def process_one(self, obj):
		if obj is None:
			return self.process_output()
		cmd = obj[0]
		pos = obj[1]
		if cmd == "feedrate":
			rate = pos
			self.queue_feedrate(rate)
		elif cmd == "position":
			self.queue_position(pos)
		elif cmd == "set_position":
			self.queue_set_position(pos)
		elif cmd == "eof":
			print("vector: EOF")
			self.queue_eof()
		else:
			self.queue_other(obj)
		return self.process_output()

	def pending(self):
		if self.pos1 is not None:
			return True
		else:
			return False

	def process_output(self):
		n = self.outq.qsize()
		if not n:
			return None, False
		elif n == 1:
			return self.outq.get_nowait(), False
		else:
			return self.outq.get_nowait(), True

	def queue_feedrate(self, rate):
		if self.pos1 is None:
			self.feedrate0 = rate
		else:
			self.feedrate1 = rate

	def queue_position(self, pos):
		if self.pos1 is None:
			self.pos1 = pos
			self.norm0 = self._norm(self._sub(pos, self.pos0))
			self.start = self.max_begin
			if self.feedrate0 is None:
				self.feedrate0 = self.max_begin # FIXME: Minimum
			if self.feedrate0 < self.start:
				self.start = self.feedrate0
			self.high = self.feedrate0
		else:
			if self.feedrate1 is None:
				self.feedrate1 = self.feedrate0
			move = self._sub(pos, self.pos1)
			if move[0] or move[1]:
				norm = self._norm(move)
				dot = self._dot(self.norm0, norm)
			else:
				# Do not interpolate Z- or feeder-only movements
				norm = [0, 0, 0, 0]
				dot = 1.0
			if dot < 0.0:
				dot = 0.0
			if self.feedrate1 <= self.max_begin:
				self.end = self.feedrate1
			else:
				self.end = self.max_begin + dot * (self.feedrate1 - self.max_begin)
			if self.end > self.high:
				self.end = self.high
			fr3 = (self.start, self.high, self.end)
			if self.last_fr3 != fr3:
				# print("vector fr3:",repr(fr3))
				self.outq.put(("feedrate3", fr3))
				self.last_fr3 = fr3
			self.outq.put(("position", self.pos1))
			self.start = self.end
			self.high = self.feedrate1
			self.norm0 = norm
			self.pos0 = self.pos1
			self.pos1 = pos
			self.feedrate0 = self.feedrate1

	def queue_set_position(self, pos):
		self.queue_eof()
		self.reset()
		self.outq.put(("set_position", pos))

	def queue_other(self, obj):
		self.outq.put(obj)

	def queue_eof(self):
		# Fake last position and reset
		if self.pos1 is not None:
			self.queue_position(self.pos1)
			pos = self.pos1
			self.reset()
			self.pos0 = pos

# Test function
if __name__ == "__main__":
	i = Interpolator(None)
	print(repr(i.process_one(("feedrate", 50))))
	print(repr(i.process_one(("position", [10, 20, 0, 2]))))
	print(repr(i.process_one(("position", [20, 25, 0, 5]))))
	print(repr(i.process_one(("feedrate", 70))))
	print(repr(i.process_one(("position", [10, 20, 0, 8]))))
	print(repr(i.process_one(("position", [20, 10, 0, 11]))))
	print(repr(i.process_one(("set_position", [20, 10, 0, 11]))))
	print(repr(i.process_one(("position", [2, 5, 0, 14]))))
	print(repr(i.process_one(("position", [3, 10, 0, 17]))))
	print(repr(i.process_one(("position", [3, 10, 0, 25]))))
	print(repr(i.process_one(("position", [3, 10, 0, 17]))))
	print(repr(i.process_one(("eof", None))))
	print(repr(i.process_one(None)))
	print(repr(i.process_one(None)))
	print(repr(i.process_one(None)))
	print(repr(i.process_one(None)))
	print(repr(i.process_one(None)))
	i = Interpolator(None)
	print(repr(i.process_one(("feedrate", 50))))
	print(repr(i.process_one(("position", [10, 20, 0, 2]))))
	print(repr(i.process_one(("eof", None))))
	print(repr(i.process_one(None)))
	print(repr(i.process_one(None)))
	i = Interpolator(None)
	print(repr(i.process_one(("feedrate", 70))))
	print(repr(i.process_one(("position", [10, 20, 0, 2]))))
	print(repr(i.process_one(("position", [20, 25, 0, 5]))))
	print(repr(i.process_one(("feedrate", 10))))
	print(repr(i.process_one(("position", [30, 30, 0, 8]))))
	print(repr(i.process_one(("position", [40, 35, 0, 11]))))
	print(repr(i.process_one(("feedrate", 50))))
	print(repr(i.process_one(("position", [50, 40, 0, 11]))))
	print(repr(i.process_one(("position", [60, 45, 0, 11]))))
	print(repr(i.process_one(("eof", None))))
	print(repr(i.process_one(None)))
	print(repr(i.process_one(None)))
	print(repr(i.process_one(None)))
	print(repr(i.process_one(None)))
