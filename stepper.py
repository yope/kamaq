#!/usr/bin/env python
#
# vim: set tabstop=4:

import alsaaudio
from math import *
import time
import sys

class Stepper(object):
	MICROSTEPS = 16
	def __init__(self, samplerate, periodsize, amplitude):
		self.periodsize = periodsize
		self.samplerate = samplerate
		self.amplitude = float(amplitude)
		steps = 4 * self.MICROSTEPS
		fsteps = float(steps)
		self.maxsteps = steps
		self.sintab = [128.0 + amplitude * sin((x * 2 * pi) / fsteps) for x in range(steps)]
		self.costab = [128.0 + amplitude * cos((x * 2 * pi) / fsteps) for x in range(steps)]
		self.sinsqtab = [128.0 + amplitude] * (steps // 2)
		self.sinsqtab += [128.0 - amplitude] * (steps // 2)
		self.cossqtab = [128.0 + amplitude] * (steps // 4)
		self.cossqtab += [128.0 - amplitude] * (steps // 2)
		self.cossqtab += [128.0 + amplitude] * (steps // 4)
		self.angle = 0.0
		self.speed = 0.0
		self.ccw = True

	def next_sample(self):
		if self.ccw:
			sint = self.sintab
			cost = self.costab
			sinst = self.sinsqtab
			cosst = self.cossqtab
		else:
			cost = self.sintab
			sint = self.costab
			cosst = self.sinsqtab
			sinst = self.cossqtab
		idx = int(self.angle)
		f1 = self.xf1
		f2 = self.xf2
		vl = f1 * sint[idx] + f2 * sinst[idx]
		vr = f1 * cost[idx] + f2 * cosst[idx]
		self.angle += self.speed
		if self.angle > self.maxsteps:
			self.angle -= float(self.maxsteps)
		return vl, vr

	def set_speed(self, speed):
		self.speed = speed
		self.xf1, self.xf2 = self._xfade(speed)

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

class StepperCluster(object):
	SAMPLERATE = 48000
	PERIODSIZE = 1024
	def __init__(self, soundcard, channels):
		self.pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, soundcard)
		self.pcm.setchannels(channels * 2)
		self.pcm.setrate(self.SAMPLERATE)
		self.pcm.setformat(alsaaudio.PCM_FORMAT_U8)
		self.pcm.setperiodsize(self.PERIODSIZE)
		self.motors = [Stepper(self.SAMPLERATE, self.PERIODSIZE, 120.0) for x in range(channels)]

	def set_home(self):
		self.position = [0.0 for x in range(channels)]

	def set_speed(self, *speed):
		assert(len(speed) <= len(self.motors))
		for i in range(len(self.motors)):
			self.motors[i].set_speed(speed[i])

	def next_sample(self):
		ret = []
		for m in self.motors:
			ret.extend(m.next_sample())
		return ret

	def _write_fsamples(self, s):
		self.pcm.write("".join(map(lambda x: chr(int(x)), s)))

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
