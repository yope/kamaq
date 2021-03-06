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

class Thermistor100k(object):
	TOFFSET = -50
	TSTEP = 10
	R100K = [8743.0, 4218.0, 2132.0, 1127.0, 620.0, 353.7, 208.6, 126.8,
				79.36, 50.96, 33.49, 22.51, 15.44, 10.80, 7.686, 5.556, 4.082,
				3.043, 2.298, 1.758, 1.360, 1.064, 0.8414, 0.6714, 0.5408,
				0.4393, 0.3597, 0.2969, 0.2468, 0.2065, 0.1740, 0.1475,
				0.1258, 0.1079, 0.09305, 0.08065]

	R1 = 1000.0
	R2 = 1000.0
	VCC = 5.16
	def __init__(self, sensor):
		self.sensor = sensor

	def read_r(self):
		vs = self.sensor.read()
		if vs <= 0.0:
			vs = 0.0001
		r = (self.VCC * self.R1) / vs - self.R1 - self.R2
		if r < 0.001:
			r = 0.001
		return r

	def read(self):
		r = self.read_r()
		for i in range(len(self.R100K)):
			r1 = self.R100K[i] * 1000.0
			if r > r1:
				break
		t0 = (i - 1) * self.TSTEP + self.TOFFSET
		t1 = i * self.TSTEP + self.TOFFSET
		r0 = self.R100K[i - 1] * 1000.0
		p = (r - r0) / (r1 - r0)
		t = t0 + (t1 - t0) * p
		return t

# Test function
if __name__ == "__main__":
	from hwmon import ScaledSensor
	from config import Config
	s = ScaledSensor(Config("kamaq.conf"), "BED")
	t = Thermistor100k(s)
	print(t.read(), "deg. Celsius")

