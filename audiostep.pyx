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

cimport cython
from libc.stdlib cimport malloc, free

cdef extern from "audiodev.h":
	DEF MAX_DIM = 4
	int audiostep_open(const char *devname, int channels, unsigned int rate)
	void set_destination(double *v)
	int main_iteration()
	void process_one_move()
	void zero_output()
	void close_audio()
	void set_feedrate(double rate)
	void set_constant_level(double *c)
	int audio_fileno()
	int push_more_audio_data()

cdef class audiostep:
	cdef int handle
	cdef double *pos
	cdef double *current
	def __init__(self, name, channels=4):
		cdef int ret
		pcmname = "surround71:CARD=" + name + ",DEV=0"
		ret = audiostep_open(pcmname, channels, 48000)
		self.pos = <double *>malloc(MAX_DIM * cython.sizeof(double))
		self.current = <double *>malloc(MAX_DIM * 2 * cython.sizeof(double))
		if self.pos is NULL:
			raise MemoryError()

	def set_destination(self, v):
		cdef int i
		for i in range(MAX_DIM):
			self.pos[i] = v[i]
		set_destination(self.pos)

	def main_iteration(self):
		return main_iteration()

	def write_more(self):
		cdef int ret
		ret = push_more_audio_data();
		if ret < -1:
			raise IOError
		elif ret == -1:
			return None
		return ret

	def process_one_move(self):
		process_one_move()

	def zero_output(self):
		zero_output()

	def close(self):
		close_audio()

	def set_feedrate(self, rate):
		set_feedrate(rate)

	def fileno(self):
		cdef int ret
		ret = audio_fileno()
		return ret

	def set_constant_current(self, c):
		cdef int i
		for i in range(MAX_DIM * 2):
			self.current[i] = c[i]
		set_constant_level(self.current)
