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

import monkeypatch
import asyncio
import os
import selectors
import time
import sys

GPIO_PATH = "gpios"

class GPIOBase(object):
	def __init__(self, name):
		self.name = name
		self.gpiodir = os.path.join(GPIO_PATH, name)
		self.gpiovalue = os.path.join(self.gpiodir, "value")

	def _write_sys(self, fname, val):
		f = open(fname, "wb")
		val = str(val) + "\n"
		f.write(val.encode("iso8859-1"))
		f.close()

class AsyncGPInput(GPIOBase):
	def __init__(self, name, callback, edge="falling", debounce=0.01):
		GPIOBase.__init__(self, name)
		self.edge = edge
		self.expt_ti = 0
		self.debounce = debounce
		self.callback = callback
		self.loop = asyncio.get_event_loop()
		self.gpio_open(name)

	def gpio_open(self, name):
		gpioedge = os.path.join(self.gpiodir, "edge")
		self._write_sys(gpioedge, self.edge)
		self.gpio_fd = os.open(self.gpiovalue, os.O_RDONLY | os.O_NONBLOCK)
		self.enable_exceptions()

	def gpio_close(self):
		self.disable_exceptions()
		os.close(self.gpio_fd)

	def enable_exceptions(self):
		self.loop.add_excepter(self.gpio_fd, self.handle_expt)

	def disable_exceptions(self):
		self.loop.remove_excepter(self.gpio_fd)

	def read_value(self):
		os.lseek(self.gpio_fd, 0, os.SEEK_SET)
		txt = os.read(self.gpio_fd, 2).strip(b" \r\n")
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

class dummy_AsyncGPInput:
	def __init__(self, name, callback, edge="falling", debounce=0.01):
		self.name = name

	def gpio_open(self, name):
		pass

	def gpio_close(self):
		pass

	def enable_exceptions(self):
		pass

	def disable_exceptions(self):
		pass

	def read_value(self):
		return 1

	def handle_expt(self):
		pass

class dummy_GPOutput:
	def __init__(self, name, initial="low"):
		self.name = name

	def config_output(self, initial):
		pass

	def set_output(self, val):
		#print("Set output", repr(self.name), "to:", repr(val))
		pass

if "--nogpio" in sys.argv:
	AsyncGPInput = dummy_AsyncGPInput
	GPOutput = dummy_GPOutput

# Test function
if __name__ == "__main__":
	class cbtest:
		def __init__(self, namein, nameout):
			self.gpi = AsyncGPInput(namein, self)
			self.gpo = GPOutput(nameout)
			self.val = True

		def gpio_event(self, name, val):
			print("GPIO Event from", name, "value:", val)
			self.gpo.set_output(self.val)
			self.val = not self.val

	cb = cbtest("endstop_X", "heater_EXT")
	asyncio.get_event_loop().run_forever()

