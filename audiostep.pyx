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

cimport cython
from libc.stdlib cimport malloc, free
cimport vector
import vector

cdef extern from "audiodev.h":
	DEF MAX_DIM = 4
	int audiostep_open(const char *devname, int channels, unsigned int rate)
	void set_destination(double *v)
	int main_iteration()
	void process_one_move()
	void zero_output()
	void close_audio()
	void set_feedrate(double begin, double high, double end)
	void set_constant_level(double *c)
	int audio_fileno()
	int push_more_audio_data()
	void stop_audio()
	void restart_audio()
	void cancel_destination()
	double *get_position()
	void set_position(double *v)
	void set_amplitude_dc(double amp)

cdef class audiostep:
	cdef int handle
	cdef double *pos
	cdef double *current
	cdef double max_feedrate
	cdef double speed_scale
	cdef vector.CmdBuffer cmdbuf
	cdef object esw
	cdef object invert

	def __cinit__(self, *args, **kwargs):
		self.pos = <double *>malloc(MAX_DIM * cython.sizeof(double))
		self.current = <double *>malloc(MAX_DIM * 2 * cython.sizeof(double))

	def __init__(self, cfg, name, channels, esw):
		cdef int ret
		pcmname = "surround71:CARD=" + name + ",DEV=0"
		bname = pcmname.encode("iso8859-1")
		ret = audiostep_open(bname, channels, 48000)
		if ret < 0:
			raise IOError
		self.max_feedrate = 0.0
		self.speed_scale = 1.0
		self.esw = esw
		self.invert = [1 - int(x) * 2 for x in cfg.settings["invert_motor"]]
		if self.pos is NULL:
			raise MemoryError()

	def connect_cmd_buffer(self, vector.CmdBuffer buf):
		self.cmdbuf = buf

	def set_speed_scale(self, double ss):
		self.speed_scale = ss

	def set_max_feedrate(self, limit):
		if limit:
			self.max_feedrate = limit
		else:
			self.max_feedrate = 0.0

	def set_destination(self, v):
		cdef int i
		for i in range(MAX_DIM):
			self.pos[i] = v[i]
		self.c_set_destination(self.pos)

	cdef void c_set_destination(self, double *pos):
		cdef int i
		cdef int inp
		self.current = get_position()
		for i, sw in enumerate(self.esw):
			inp = sw.read_value()
			if not inp and self.current[i] > pos[i] * self.invert[i]:
				pos[i] = self.current[i]
		# print "AUDIOSTEP: c_set_destination:", pos[0], pos[1], pos[2], pos[3]
		set_destination(pos)

	def set_position(self, v):
		cdef int i
		for i in range(MAX_DIM):
			self.pos[i] = v[i]
		set_position(self.pos)

	def set_home(self):
		cdef int i
		for i in range(MAX_DIM):
			self.pos[i] = 0.0
		set_position(self.pos)

	def get_position(self):
		cdef double *pos
		ret = []
		pos = get_position()
		for i in range(MAX_DIM):
			ret.append(pos[i])
		return ret

	def main_iteration(self):
		return main_iteration()

	def write_more(self):
		"""
		Write more data to audio device. returns:
		 - None if destination was reached (action needed).
		 - negative error code
		 - positive amount of data written to audio device
		"""
		cdef int ret
		ret = push_more_audio_data()
		if ret < -1:
			raise IOError
		elif ret == -1:
			return None
		return ret

	def pull_cmd_buffer(self):
		cdef int ret = 0
		cdef int cmd[1]
		cdef double pos[4]
		ret = push_more_audio_data()
		while ret == -1: # Destination reached
			ret = self.cmdbuf.pop(cmd, pos)
			if ret != 0:
				return ret
			self.handle_command(cmd[0], pos)
			ret = push_more_audio_data()
		if ret < -1:
			raise IOError
		return 0

	cdef void handle_command(self, int cmd, double *pos):
		# print "AUDIOSTEP: handle_command:", cmd
		if cmd == vector.FEEDRATE:
			self.set_feedrate(pos[0], pos[0], pos[0])
		elif cmd == vector.FEEDRATE3:
			self.set_feedrate(pos[0], pos[1], pos[2])
		elif cmd == vector.POSITION:
			self.c_set_destination(pos)
		elif cmd == vector.SET_POSITION:
			set_position(pos)
		else:
			print "AUDIOSTEP: Unknown command id:", cmd

	def process_one_move(self):
		process_one_move()

	def zero_output(self):
		zero_output()

	def stop(self):
		stop_audio()

	def restart(self):
		restart_audio()

	def close(self):
		close_audio()

	def cancel_destination(self):
		cancel_destination()

	cpdef set_feedrate(self, double begin, double high, double end):
		cdef double fr[3]
		fr[0] = begin
		fr[1] = high
		fr[2] = end
		for i in range(3):
			fr[i] *= self.speed_scale
			if self.max_feedrate > 0.0 and fr[i] > self.max_feedrate:
				fr[i] = self.max_feedrate
			fr[i] /= 600.0
		# print "AUDIOSTEP: set_feedrate:", fr[0], fr[1], fr[2]
		set_feedrate(fr[0], fr[1], fr[2])

	def fileno(self):
		cdef int ret
		ret = audio_fileno()
		return ret

	def set_constant_current(self, c):
		cdef int i
		for i in range(MAX_DIM * 2):
			self.current[i] = c[i]
		set_constant_level(self.current)

	def set_amplitude_dc(self, amp):
		set_amplitude_dc(amp)
