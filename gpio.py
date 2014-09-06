#!/usr/bin/env python
#
# Copyright (c) 2014 David Jander
#
# Contains code derived from the Python asyncore library
# Copyright 1996 by Sam Rushing
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# vim: set tabstop=4:

import asyncore
import os
import select
import time

GPIO_PATH = "gpios"

# New poll function for asyncore with excepption-only mode:
def asyncore_poll_with_except(timeout=0.0, map=None):
	if map is None:
		map = socket_map
	if map:
		r = []; w = []; e = []
		for fd, obj in map.items():
			is_r = obj.readable()
			is_w = obj.writable()
			is_e = obj.exceptable()
			if is_r:
				r.append(fd)
			if is_w:
				w.append(fd)
			if is_e:
				e.append(fd)
		if [] == r == w == e:
			time.sleep(timeout)
			return

		try:
			r, w, e = select.select(r, w, e, timeout)
		except select.error, err:
			if err.args[0] != EINTR:
				raise
			else:
				return

		for fd in r:
			obj = map.get(fd)
			if obj is None:
				continue
			asyncore.read(obj)

		for fd in w:
			obj = map.get(fd)
			if obj is None:
				continue
			asyncore.write(obj)

		for fd in e:
			obj = map.get(fd)
			if obj is None:
				continue
			asyncore._exception(obj)

asyncore.poll = asyncore_poll_with_except

class AsyncGPInput(asyncore.file_dispatcher):
	def __init__(self, name, callback, edge="falling"):
		self.name = name
		self.edge = edge
		self.callback = callback
		self.gpio_open(name)
		asyncore.file_dispatcher.__init__(self, self.gpio_fd)

	def _write_sys(self, fname, val):
		f = open(fname, "wb")
		f.write(str(val) + "\n")
		f.close()

	def gpio_open(self, name):
		gpiodir = os.path.join(GPIO_PATH, name)
		gpiovalue = os.path.join(gpiodir, "value")
		gpioedge = os.path.join(gpiodir, "edge")
		self._write_sys(gpioedge, self.edge)
		self.gpio_fd = os.open(gpiovalue, os.O_RDONLY | os.O_NONBLOCK)
		self.enable_exceptions()

	def gpio_close(self):
		os.close(self.gpio_fd)

	def writable(self):
		return False

	def readable(self):
		return False

	def exceptable(self):
		return self.enabled

	def enable_exceptions(self):
		self.enabled = True

	def disable_exceptions(self):
		self.enabled = True

	def read_value(self):
		os.lseek(self.gpio_fd, 0, os.SEEK_SET)
		txt = os.read(self.gpio_fd, 2).strip(" \r\n")
		return int(txt)

	def handle_expt(self):
		self.callback.gpio_event(self.name)

# Test function
if __name__ == "__main__":
	class cbtest:
		def __init__(self, name):
			self.gpi = AsyncGPInput(name, self)

		def gpio_event(self, name):
			print "GPIO Event from", name, "value:", self.gpi.read_value()
			self.gpi.disable_exceptions()
			time.sleep(0.1) # Debounce
			self.gpi.enable_exceptions()
	cb = cbtest("endstop_X")
	asyncore.loop()

