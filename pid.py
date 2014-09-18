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

import time

class PidController(object):
	def __init__(self, sensor, actuator, P, I, D, period=1.0):
		self.sensor = sensor
		self.actuator = actuator
		self.P = P
		self.I = I * period
		self.D = D / period
		self.integ = 0.0
		self.setpoint = 0
		self.err0 = 0.0
		self.output = 0.0
		self.period = period
		self.windup_limit = 100.0

	def set_setpoint(self, sp):
		self.setpoint = sp

	def iteration(self):
		err = self.setpoint - self.sensor.read()
		derr = err - self.err0
		self.err0 = err
		self.integ += err
		if self.integ > self.windup_limit:
			self.integ = self.windup_limit
		if self.integ < -self.windup_limit:
			self.integ = -self.windup_limit
		self.output = self.P * err + self.I * self.integ + self.D * derr
		if self.output > 1.0:
			self.output = 1.0
		if self.output < 0.0:
			self.output = 0.0
		ontime = self.output * self.period
		if ontime > 0.0:
			self.actuator.set_output(1)
		time.sleep(ontime)
		if ontime < self.period:
			self.actuator.set_output(0)
			time.sleep(self.period - ontime)

	def get_output(self):
		return self.output

if __name__ == "__main__":
	from temp100k import Thermistor100k
	from hwmon import ScaledSensor
	from config import Config
	from gpio import GPOutput
	s = ScaledSensor(Config("grunner.conf"), "EXT")
	t = Thermistor100k(s)
	o = GPOutput("heater_EXT")
	p = PidController(t, o, 0.5, 0.001, 0.5)
	sp = 30
	p.set_setpoint(sp)
	while True:
		p.iteration()
		print "Temp =", t.read(), "setpoint =", sp, "Ouput =", p.get_output()
