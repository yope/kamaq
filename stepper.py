#!/usr/bin/env python
#
# vim: set tabstop=4:

import alsaaudio
from math import *
import time
import sys
import struct
import time
from math import *

class Stepper(object):
	MICROSTEPS = 16
	def __init__(self, samplerate, periodsize, amplitude, offset):
		self.periodsize = periodsize
		self.samplerate = samplerate
		self.amplitude = float(amplitude)
		steps = 4 * self.MICROSTEPS
		fsteps = float(steps)
		self.maxsteps = steps
		self.sintab = [offset + amplitude * sin((x * 2 * pi) / fsteps) for x in range(steps)]
		self.costab = [offset + amplitude * cos((x * 2 * pi) / fsteps) for x in range(steps)]
		self.sinsqtab = [offset + amplitude] * (steps // 2)
		self.sinsqtab += [offset - amplitude] * (steps // 2)
		self.cossqtab = [offset + amplitude] * (steps // 4)
		self.cossqtab += [offset - amplitude] * (steps // 2)
		self.cossqtab += [offset + amplitude] * (steps // 4)
		self.angle = 0.0
		self.speed = 0.0
		self.offset = offset
		self.ccw = True
		self.set_speed(0)

	def do_step(self, direction):
		idx = self.angle
		idx += direction
		if idx >= self.steps:
			idx -= self.steps
		elif idx < 0:
			idx += self.steps
		f1 = self.xf1
		f2 = self.xf2
		vl = f1 * sint[idx] + f2 * sinst[idx]
		vr = f1 * cost[idx] + f2 * cosst[idx]
		self.angle = idx
		return vl, vr

	# FIXME: Deprecated
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

	# FIXME: Deprecated
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

class StepperCluster(object):
	SAMPLERATE = 44100
	PERIODSIZE = 1024
	def __init__(self, soundcard, channels):
		cards = alsaaudio.cards()
		if not soundcard in cards:
			print "Error: did not find soundcard named:", soundcard
			raise ValueError
		pcmname = "surround71:CARD=" + soundcard + ",DEV=0"
		self.pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, pcmname)
		self.pcm.setchannels(channels * 2)
		self.pcm.setrate(self.SAMPLERATE)
		self.pcm.setformat(alsaaudio.PCM_FORMAT_U16_LE)
		self.pcm.setperiodsize(self.PERIODSIZE)
		self.motors = [Stepper(self.SAMPLERATE, self.PERIODSIZE, 32767, 0) for x in range(channels)]
		self.dim = len(self.motors)
		self.packer = struct.Struct("<" + "hh" * channels)
		self.set_home()
		self.set_destination(self.position)
		self.max_speeds = [5.0 for x in range(self.dim)]

	def set_home(self):
		self.position = [0.0 for x in range(self.dim)]

	def _vec_diff(self, v1, v2):
		return map(lambda x, y: x - y, v1, v2)

	def _vec_sum(self, v1, v2):
		return map(lambda x, y: x + y, v1, v2)

	def _vec_mul_scalar(self, v, fact):
		return [x * fact for x in v]

	def _vec_dist(self, v1, v2):
		d = self._vec_diff(v1, v2)
		sqd = sum([x * x for x in d])
		return sqrt(sqd)

	def set_destination(self, *v):
		if len(v) == 1:
			v = v[0]
		self.origin = self.position
		self.destination = v
		self.time = 0
		self.delta_t = 0.2 # FIXME: Start speed
		self.dist = self._vec_dist(self.position, v)
		if self.dist == 0:
			self.incvec = [0 for x in range(self.dim)]
			return
		dif = self._vec_diff(v, self.origin)
		self.incvec = [x / self.dist for x in dif]

	def next_position(self, incr = 1):
		self.time += incr
		newp = self._vec_mul_scalar(self.incvec, self.time)
		newp = self._vec_sum(newp, self.origin)
		err = self._vec_diff(newp, self.position)
		steps = [int(x) for x in err]
		self.position = self._vec_sum(self.position, steps)
		return steps

	def pos_iteration(self):
		ret = self.next_position(self.delta_t)
		dtinc = 0.1
		dt = self.dist - self.time
		if ((self.delta_t - 0.2) / (dtinc * 2)) >= dt:
			self.delta_t -= dtinc
		elif self.delta_t < (1.0 - dtinc):
			self.delta_t += dtinc
		return ret

	# FIXME: Deprecated
	def set_speed(self, *speed):
		assert(len(speed) <= len(self.motors))
		for i in range(len(self.motors)):
			self.motors[i].set_speed(speed[i])

def main_test_dc():
	c = StepperCluster('Device', 4)
	#data = "\x00\x80\x80\x80\x80\x80\x80\x80" * c.PERIODSIZE
	data = [x * 32 * 255 for x in range(8)]
	for i in range(len(sys.argv)):
		if not i:
			continue
		data[i-1] = float(sys.argv[i]) * 255.0
	print repr(data)
	data = c.packer.pack(*data) * c.PERIODSIZE
	while True:
		ti = time.time()
		c.pcm.write(data)
		ti = time.time() - ti
		print "Sample rate:", c.PERIODSIZE/ti
	c.pcm.close()

def main_test_pos():
	c = StepperCluster('Device', 4)
	c.set_destination(10, 8, 5, 2)
	print repr(c.incvec)
	t = 0
	while c.time < c.dist and t < 100:
		s = c.pos_iteration()
		print "Position:", c.position, "Steps:", s, "speed:", c.delta_t
		t += 1
	c.set_destination(-1, -10, 5, 2)
	print repr(c.incvec)
	t = 0
	while c.time < c.dist and t < 100:
		s = c.pos_iteration()
		print "Position:", c.position, "Steps:", s, "speed:", c.delta_t
		t += 1

if __name__ == "__main__":
	main_test_pos()

