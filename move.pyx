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

from libc.math cimport sqrt

cimport vector
import vector

cdef class Move(object):
	cdef double mm2steps[4]
	cdef int dim
	cdef vector.CmdBuffer output_buffer
	cdef double last_pos[4]
	cdef double last_mpos[4]
	cdef double feedrate, feedrate0, orig_feedrate
	cdef vector.Interpolator inter
	cdef object motor_name
	cdef object print_volume
	cdef object motor_name_indexes
	cdef object printer

	def __init__(self, cfg, printer):
		cdef int i
		self.dim = cfg.settings["num_motors"]
		for i in range(self.dim):
			self.mm2steps[i] = float(cfg.settings["steps_per_mm"][i] * (1 - int(cfg.settings["invert_motor"][i]) * 2))
		self.motor_name = cfg.settings["motor_name"]
		self.print_volume = cfg.settings["print_volume"]
		self.motor_name_indexes = {}
		for i in range(len(self.motor_name)):
			self.motor_name_indexes[self.motor_name[i]] = i
		self.printer = printer
		self.output_buffer = vector.CmdBuffer()
		self.inter = vector.Interpolator()
		self.reset()

	def reset(self):
		cdef int i
		self.feedrate = 0.0
		self.feedrate0 = 0.0
		self.orig_feedrate = 0.0
		for i in range(self.dim):
			self.last_pos[i] = 0.0
			self.last_mpos[i] = 0.0
		self.inter.reset()

	cdef void transform(self, double *gpos, double *ret):
		cdef int i
		for i in range(self.dim):
			ret[i] = gpos[i] * self.mm2steps[i]

	def reverse_transform(self, scpos):
		cdef int i
		ret = []
		for i in range(self.dim):
			ret.append(scpos[i] / self.mm2steps[i])
		return ret

	cdef double _dist(self, double *vec):
		cdef int i
		cdef double ret = 0.0
		for i in range(self.dim):
			ret += vec[i] * vec[i]
		return sqrt(ret)

	cdef void _sub(self, double *vec1, double *vec2, double *ret):
		cdef int i
		for i in range(4):
			ret[i] = vec1[i] - vec2[i]

	def set_feedrate(self, double fr):
		self.feedrate = fr
		self.orig_feedrate = fr

	def get_feedrate(self):
		return self.feedrate

	cdef void transform_feedrate(self, double *po, double *pt):
		cdef double dpo, sf
		dpo = self._dist(po)
		if dpo:
			sf = (self._dist(pt) / dpo) / 80.0
		else:
			sf = 1.0
		self.feedrate = sf * self.orig_feedrate

	cdef void push_homing(self, axes):
		cdef int i, j
		cdef double p[4]
		cdef double pos[4]
		cdef double frb[4]
		cdef double zerop[4]
		for i in range(self.dim):
			zerop[i] = 0.0
		self.inter.process_one(vector.SET_POSITION, zerop)
		for i in axes:
			for j in range(self.dim):
				pos[j] = 0.0
			pos[i] = -self.print_volume[i]
			self.transform(pos, p)
			if i < 2:
				self.set_feedrate(50.0)
			else:
				self.set_feedrate(1.5)
			self.transform_feedrate(pos, p)
			frb[0] = self.feedrate
			self.inter.process_one(vector.FEEDRATE, frb)
			self.inter.process_one(vector.POSITION, p)
			self.inter.process_one(vector.SET_POSITION, zerop)
			if i < 2:
				pos[i] = 4
			else:
				pos[i] = 2
			self.transform(pos, p)
			self.inter.process_one(vector.POSITION, p)
			if i < 2:
				self.set_feedrate(4.0)
			else:
				self.set_feedrate(1.0)
			pos[i] = -6
			self.transform(pos, p)
			self.transform_feedrate(pos, p)
			frb[0] = self.feedrate
			self.inter.process_one(vector.FEEDRATE, frb)
			self.inter.process_one(vector.POSITION, p)
			self.inter.process_one(vector.SET_POSITION, zerop)

	def get_output_buffer(self):
		return self.output_buffer

	def buffer_ready(self):
		ret = True
		if self.output_buffer.space() <= 2:
			ret = False
		if not self.inter.buffer_ready():
			ret = False
		return ret

	def process_command(self, obj):
		cdef int i
		cdef double pos[4]
		cdef double p[4]
		cdef double tmp1[4]
		cdef double tmp2[4]
		cdef double frb[4]
		cdef int icmd[1]
		cdef int imore[1]
		cmd = obj["command"]
		# print "MOVE: process command:", repr(obj)
		if cmd == "position":
			for i in range(self.dim):
				pos[i] = 0.0
			for w in obj:
				idx = self.motor_name_indexes.get(w, None)
				if idx is not None:
					pos[idx] = obj[w]
				elif w == "F":
					self.set_feedrate(obj[w])
			self.printer.set_position_mm(pos[0], pos[1], pos[2], pos[3])
			self.transform(pos, p)
			self._sub(pos, self.last_pos, tmp1)
			self._sub(p, self.last_mpos, tmp2)
			self.transform_feedrate(tmp1, tmp2)
			if self.feedrate != self.feedrate0:
				self.feedrate0 = self.feedrate
				frb[0] = self.feedrate
				self.inter.process_one(vector.FEEDRATE, frb)
			self.inter.process_one(vector.POSITION, p)
			for i in range(self.dim):
				self.last_pos[i] = pos[i]
				self.last_mpos[i] = p[i]
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
			self.push_homing(axes)
		elif cmd == "setpoint":
			pass
		elif cmd == "set_position":
			for i in range(self.dim):
				pos[i] = self.last_pos[i]
			for w in obj:
				idx = self.motor_name_indexes.get(w, None)
				if idx is not None:
					pos[idx] = obj[w]
			self.printer.set_position_mm(pos[0], pos[1], pos[2], pos[3])
			self.transform(pos, p)
			self.inter.process_one(vector.SET_POSITION, p)
		elif cmd == "eof":
			self.inter.process_one(vector.EOF, pos)

		while True:
			self.inter.process_output(icmd, pos, imore)
			if icmd[0] == vector.NOP:
				break
			# print "MOVE: Push command:", icmd[0]
			self.output_buffer.push(icmd[0], pos)
			if imore[0] == 0:
				break
