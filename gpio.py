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

class GPIOBase(object):
	def __init__(self, name):
		self.name = name
		self.gpiodir = os.path.join(GPIO_PATH, name)
		self.gpiovalue = os.path.join(self.gpiodir, "value")

	def _write_sys(self, fname, val):
		f = open(fname, "wb")
		f.write(str(val) + "\n")
		f.close()

class AsyncGPInput(asyncore.file_dispatcher, GPIOBase):
	def __init__(self, name, callback, edge="falling", debounce=0.01):
		GPIOBase.__init__(self, name)
		self.edge = edge
		self.expt_ti = 0
		self.debounce = debounce
		self.callback = callback
		self.gpio_open(name)
		asyncore.file_dispatcher.__init__(self, self.gpio_fd)

	def gpio_open(self, name):
		gpioedge = os.path.join(self.gpiodir, "edge")
		self._write_sys(gpioedge, self.edge)
		self.gpio_fd = os.open(self.gpiovalue, os.O_RDONLY | os.O_NONBLOCK)
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
		ti = time.time()
		val = self.read_value()
		if not self.expt_ti:
			self.expt_ti = ti + self.debounce
			return
		if self.expt_ti > ti:
			return
		self.expt_ti = ti + self.debounce
		self.callback.gpio_event(self.name, val)

class GPOutput(GPIOBase):
	def __init__(self, name, initial="low"):
		GPIOBase.__init__(self, name)
		self.config_output(initial)

	def config_output(self, initial):
		gpiodir = os.path.join(self.gpiodir, "direction")
		self._write_sys(gpiodir, initial)

	def set_output(self, val):
		self._write_sys(self.gpiovalue, int(val))

# Test function
if __name__ == "__main__":
	class cbtest:
		def __init__(self, namein, nameout):
			self.gpi = AsyncGPInput(namein, self)
			self.gpo = GPOutput(nameout)
			self.val = True

		def gpio_event(self, name, val):
			print "GPIO Event from", name, "value:", val
			self.gpo.set_output(self.val)
			self.val = not self.val

	cb = cbtest("endstop_X", "heater_EXT")
	asyncore.loop()

