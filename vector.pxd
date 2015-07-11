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

cdef class CmdBuffer:
	cdef int cmd[32]
	cdef double pos[32][4]
	cdef int fill_idx
	cdef int empty_idx
	cdef int max_idx

	cdef void reset(self)
	cdef int size(self)
	cdef int space(self)
	cdef int full(self)
	cdef int push(self, int cmd, double *pos)
	cdef int pop(self, int *cmd, double *pos)

cdef class Interpolator:
	cdef double feedrate0
	cdef double max_begin
	cdef double start
	cdef double high
	cdef double end
	cdef double feedrate1
	cdef double pos0[4]
	cdef double pos1[4]
	cdef double norm0[4]
	cdef double last_fr3[3]
	cdef int pos1_valid
	cdef CmdBuffer outq

	cdef void reset(self)
	cdef double _dist(self, double *vec)
	cdef void _sub(self, double *vec1, double *vec2, double *res)
	cdef void _norm(self, double *vec, double *res)
	cdef double _dot(self, double *vec1, double *vec2)
	cdef int buffer_ready(self)
	cdef void process_one(self, int cmd, double *pos)
	cdef int pending(self)
	cdef void process_output(self, int *cmd, double *pos, int *more)
	cdef void queue_feedrate(self, double *rate)
	cdef void queue_position(self, double *pos)
	cdef void queue_set_position(self, double *pos)
	cdef void queue_eof(self)
	cdef void queue_endstop(self, double *pos)

cdef enum:
	NOP,
	FEEDRATE,
	FEEDRATE3,
	POSITION,
	SET_POSITION,
	ENDSTOP,
	EOF
