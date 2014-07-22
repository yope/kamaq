#!/usr/bin/env python
#
# vim: set tabstop=4:

import alsaaudio
from math import *
import time
import sys

class Stepper(object):
	def __init__(self):
		self.pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL)
		self.pcm.setchannels(2)
		self.pcm.setrate(48000)
		self.pcm.setformat(alsaaudio.PCM_FORMAT_U8)
		self.pcm.setperiodsize(1024)
		amp = 120.0
		self.sintab = [128.0 + amp * sin((x * 2 * pi) / 1024.0) for x in range(1024)]
		self.costab = [128.0 + amp * cos((x * 2 * pi) / 1024.0) for x in range(1024)]
		self.sinsqtab = [128.0 + amp] * 512 + [128.0 - amp] * 512
		self.cossqtab = [128.0 + amp] * 256 + [128.0 - amp] * 512 + [128.0 + amp] * 256

	def getsin(self, x):
		return self.sintab[int(x) % 1024]

	def getcos(self, x):
		return self.costab[int(x) % 1024]

	def _xfade(self, speed):
		if speed < 2.0:
			return 1.0, 0.0
		elif speed < 4.0:
			d = (speed - 2.0) / 2.0
			return 1.0 - d, d
		else:
			return 0.0, 1.0

	def move(self, steps, initial_speed = 2.0, final_speed = 4.0):
		if steps > 0:
			sint = self.sintab
			cost = self.costab
			sinst = self.sinsqtab
			cosst = self.cossqtab
		else:
			cost = self.sintab
			sint = self.costab
			cosst = self.sinsqtab
			sinst = self.cossqtab
			steps = -steps
		per = t = n = 0
		j = initial_speed
		data = ""
		ramp = 0.2
		nramp = (final_speed - initial_speed) / ramp
		f1, f2 = self._xfade(j)
		while n < steps:
			t += j
			if t >= 1024:
				t -= 1024
				n += 1
				if n < nramp:
					j += ramp
				elif n > (steps-nramp):
					j -= ramp
				f1, f2 = self._xfade(j)
			idx = int(t)
			vl = f1 * sint[idx] + f2 * sinst[idx]
			vr = f1 * cost[idx] + f2 * cosst[idx]
			data += chr(int(vl)) + chr(int(vr))
			if len(data) >= 1024:
				self.pcm.write(data)
				data = ""
		if 0 < len(data) < 1024:
			c = data[-1]
			data += c * (1024-len(data))
		self.pcm.write(data)

if __name__ == "__main__":
	maxspeed = 5.0
	if len(sys.argv) > 1:
		maxspeed = float(sys.argv[1])
	s = Stepper()
	while True:
		s.move(201, 1.0, maxspeed)
		time.sleep(0.2)
		s.move(-201, 1.0, 1.5)
		time.sleep(0.2)
