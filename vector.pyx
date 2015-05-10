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

from libc.math cimport sqrt

cdef class CmdBuffer:
	def __init__(self):
		self.reset()
		self.max_idx = 32

	cdef void reset(self):
		self.fill_idx = 0
		self.empty_idx = 0

	cdef int size(self):
		cdef int d = self.fill_idx - self.empty_idx
		if d < 0:
			d += 32
		return d

	cdef int space(self):
		return (self.max_idx - self.size() - 1)

	cdef int full(self):
		if (self.fill_idx + 1) & 31 == self.empty_idx:
			return 1
		return 0

	cdef int push(self, int cmd, double *pos):
		cdef int i
		# print "BUFFER: push", cmd
		if self.full():
			print "BUFFER: push: FULL! cmd =", cmd, "space =", self.space()
			return 1
		self.cmd[self.fill_idx] = cmd
		for i in range(4):
			self.pos[self.fill_idx][i] = pos[i]
		self.fill_idx = (self.fill_idx + 1) & 31
		return 0

	cdef int pop(self, int *cmd, double *pos):
		cdef int i
		if self.empty_idx == self.fill_idx:
			print "BUFFER: pop: EMPTY!"
			return 1
		cmd[0] = self.cmd[self.empty_idx]
		for i in range(4):
			pos[i] = self.pos[self.empty_idx][i]
		self.empty_idx = (self.empty_idx + 1) & 31
		# print "BUFFER: pop", cmd[0]
		return 0

	def ppush(self, cmd, pos):
		cdef double cpos[4]
		cdef int i
		for i in range(4):
			cpos[i] = pos[i]
		ret = self.push(<int>cmd, cpos)
		return ret

	def ppop(self):
		cdef double cpos[4]
		cdef int i
		cdef int cmd[1]
		pos = []
		ret = self.pop(cmd, cpos)
		if ret:
			return None
		pcmd = cmd[0]
		for i in range(4):
			pos.append(cpos[i])
		return pcmd, pos

cdef class Interpolator:
	def __init__(self):
		self.max_begin = 12.0 # FIXME
		self.feedrate0 = -1.0
		self.start = 0.0
		self.high = 0.0
		self.end = 0.0
		self.outq = CmdBuffer()
		self.reset()

	cdef void reset(self):
		cdef int i
		self.feedrate1 = -1.0
		for i in range(4):
			self.pos0[0] = 0.0
			self.norm0[0] = 0.0
		self.pos1_valid = 0
		self.last_fr3[0] = -1.0

	cdef double _dist(self, double *vec):
		cdef int i
		cdef double ret = 0.0
		for i in range(4):
			ret += vec[i] * vec[i]
		return sqrt(ret)

	cdef void _sub(self, double *vec1, double *vec2, double *res):
		cdef int i
		for i in range(4):
			res[i] = vec1[i] - vec2[i]

	cdef void _norm(self, double *vec, double *res):
		cdef int i
		cdef double d
		d = self._dist(vec)
		if d == 0.0:
			d = 1.0 # We cannot normalize a vector of zero length...
		for i in range(4):
			res[i] = vec[i] / d

	cdef double _dot(self, double *vec1, double *vec2):
		cdef int i
		cdef double ret = 0.0
		for i in range(4):
			ret += vec1[i] * vec2[i]
		return ret

	cdef int buffer_ready(self):
		if self.outq.space() >= 2: # At lease one feedrate and one pos command
			return 1
		return 0

	cdef void process_one(self, int cmd, double *pos):
		cdef int s = self.outq.space()
		if s <= 2:
			print "INTER: Warning, not enough space in buffer! space =", s
		if cmd == NOP:
			return
		if cmd == FEEDRATE:
			self.queue_feedrate(pos)
		elif cmd == POSITION:
			self.queue_position(pos)
		elif cmd == SET_POSITION:
			self.queue_set_position(pos)
		elif cmd == EOF:
			print "vector: EOF"
			self.queue_eof()
		else:
			print "Vector: Unsupported command:", cmd

	cdef int pending(self):
		return self.pos1_valid

	cdef void process_output(self, int *cmd, double *pos, int *more):
		cdef int n = self.outq.size()
		if n == 0:
			cmd[0] = NOP
			more[0] = 0
		elif n == 1:
			more[0] = 0
			self.outq.pop(cmd, pos)
		else:
			more[0] = 1
			self.outq.pop(cmd, pos)

	cdef void queue_feedrate(self, double *rate):
		if self.pos1_valid == 0:
			self.feedrate0 = rate[0]
		else:
			self.feedrate1 = rate[0]

	cdef void queue_position(self, double *pos):
		cdef int i
		cdef double res[4]
		cdef double move[4]
		cdef double norm[4]
		cdef double dot
		if self.pos1_valid == 0:
			for i in range(4):
				self.pos1[i] = pos[i]
			self._sub(pos, self.pos0, res)
			self._norm(res, res)
			self.start = self.max_begin
			if self.feedrate0 < 0.0:
				self.feedrate0 = self.max_begin # FIXME: Minimum
			if self.feedrate0 < self.start:
				self.start = self.feedrate0
			self.high = self.feedrate0
			self.pos1_valid = 1
		else:
			if self.feedrate1 < 0.0:
				self.feedrate1 = self.feedrate0
			self._sub(pos, self.pos1, move)
			if move[0] != 0.0 or move[1] != 0.0:
				self._norm(move, norm)
				dot = self._dot(self.norm0, norm)
			else:
				# Do not interpolate Z- or feeder-only movements
				for i in range(4):
					norm[i] = 0.0
				dot = 0.0
			if dot < 0.0:
				dot = 0.0
			if self.feedrate1 <= self.max_begin:
				self.end = self.feedrate1
			else:
				self.end = self.max_begin + dot * (self.feedrate1 - self.max_begin)
			if self.end > self.high:
				self.end = self.high
			if self.last_fr3[0] != self.start or self.last_fr3[1] != self.high or self.last_fr3[2] != self.end:
				self.last_fr3[0] = self.start
				self.last_fr3[1] = self.high
				self.last_fr3[2] = self.end
				self.outq.push(FEEDRATE3, self.last_fr3)
			self.outq.push(POSITION, self.pos1)
			self.start = self.end
			self.high = self.feedrate1
			for i in range(4):
				self.norm0[i] = norm[i]
				self.pos0[i] = self.pos1[i]
				self.pos1[i] = pos[i]
			self.feedrate0 = self.feedrate1

	cdef void queue_set_position(self, double *pos):
		self.queue_eof()
		self.reset()
		self.outq.push(SET_POSITION, pos)

	cdef void queue_eof(self):
		cdef int i
		cdef double pos[4]
		# Fake last position and reset
		if self.pos1_valid:
			self.queue_position(self.pos1)
			for i in range(4):
				pos[i] = self.pos1[i]
			self.reset()
			for i in range(4):
				self.pos0[i] = pos[i]
