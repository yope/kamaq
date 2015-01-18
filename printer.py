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

from temp100k import Thermistor100k
from hwmon import ScaledSensor
from gpio import GPOutput
from pid import PidController

class Printer(object):
	def __init__(self, cfg):
		self.cfg = cfg
		self.webui = None
		self.pid = {}
		for n in ["ext", "bed"]:
			name = n.upper()
			o = GPOutput("heater_" + name)
			s = ScaledSensor(self.cfg, name)
			t = Thermistor100k(s)
			self.pid[n] = PidController(t, o, 0.3, 0.004, 0.5)

	def add_webui(self, webui):
		self.webui = webui

	def launch_pid(self, name, sp):
		self.pid[name].spawn()
		self.set_setpoint(name, sp)

	def shutdown(self):
		for name in self.pid:
			self.pid[name].set_setpoint(0)
			self.pid[name].shutdown()

	def set_setpoint(self, name, sp):
		self.pid[name].set_setpoint(sp)

	def get_temperature(self, name):
		return self.pid[name].get_input()

	def set_position_mm(self, x, y, z, e):
		if self.webui:
			self.webui.queue_move(x, y, z, e)
