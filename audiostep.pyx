#!/usr/bin/env python
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

cdef class audiostep:
	cdef int handle
	cdef double *pos
	def __init__(self, name, channels=4):
		cdef int ret
		pcmname = "surround71:CARD=" + name + ",DEV=0"
		ret = audiostep_open(pcmname, channels, 48000)
		self.pos = <double *>malloc(MAX_DIM*cython.sizeof(double))
		if self.pos is NULL:
			raise MemoryError()

	def set_destination(self, v):
		cdef int i
		for i in range(MAX_DIM):
			self.pos[i] = v[i]
		set_destination(self.pos)

	def main_iteration(self):
		return main_iteration()

	def process_one_move(self):
		process_one_move()

	def zero_output(self):
		zero_output()

	def close(self):
		close_audio()

	def set_feedrate(self, rate):
		set_feedrate(rate)

