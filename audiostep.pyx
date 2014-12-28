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
	def __init__(self, name, channels=4):
		cdef int ret
		pcmname = "surround71:CARD=" + name + ",DEV=0"
		bname = pcmname.encode("iso8859-1")
		ret = audiostep_open(bname, channels, 48000)
		self.pos = <double *>malloc(MAX_DIM * cython.sizeof(double))
		self.current = <double *>malloc(MAX_DIM * 2 * cython.sizeof(double))
		if self.pos is NULL:
			raise MemoryError()

	def set_destination(self, v):
		cdef int i
		for i in range(MAX_DIM):
			self.pos[i] = v[i]
		set_destination(self.pos)

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

	def stop(self):
		stop_audio()

	def restart(self):
		restart_audio()

	def close(self):
		close_audio()

	def cancel_destination(self):
		cancel_destination()

	def set_feedrate(self, begin, high, end):
		set_feedrate(begin, high, end)

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
