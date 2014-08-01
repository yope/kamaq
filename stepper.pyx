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

cdef class Stepper(object):
	cdef int periodsize, samplerate, angle, maxsteps
	cdef double amplitude, speed, offset, xf1, xf2
	cdef int MICROSTEPS
	cdef double sintab[64], costab[64]
	cdef int ccw
	def __init__(self, int samplerate, int periodsize, double amplitude, double offset):
		cdef int steps
		cdef double fsteps
		cdef int x
		self.MICROSTEPS = 16
		self.periodsize = periodsize
		self.samplerate = samplerate
		self.amplitude = float(amplitude)
		steps = 4 * self.MICROSTEPS
		fsteps = float(steps)
		self.maxsteps = steps
		for x in range(steps):
			self.sintab[x] = offset + amplitude * sin((x * 2 * pi) / fsteps)
			self.costab[x] = offset + amplitude * cos((x * 2 * pi) / fsteps)
		#self.sintab = [offset + amplitude * sin((x * 2 * pi) / fsteps) for x in range(steps)]
		#self.costab = [offset + amplitude * cos((x * 2 * pi) / fsteps) for x in range(steps)]
		#self.sinsqtab = [offset + amplitude] * (steps // 2)
		#self.sinsqtab += [offset - amplitude] * (steps // 2)
		#self.cossqtab = [offset + amplitude] * (steps // 4)
		#self.cossqtab += [offset - amplitude] * (steps // 2)
		#self.cossqtab += [offset + amplitude] * (steps // 4)
		self.angle = 0
		self.speed = 0.0
		self.offset = offset
		self.ccw = True
		self.set_speed(0)

	def do_step(self, int direction):
		cdef double vl, vr
		cdef int idx
		idx = self.angle
		idx += direction
		if idx >= self.maxsteps:
			idx -= self.maxsteps
		elif idx < 0:
			idx += self.maxsteps
		#f1 = self.xf1
		#f2 = self.xf2
		#vl = f1 * self.sintab[idx] + f2 * self.sinsqtab[idx]
		#vr = f1 * self.costab[idx] + f2 * self.cossqtab[idx]
		vl = self.sintab[idx]
		vr = self.costab[idx]
		self.angle = idx
		return vl, vr

	def set_speed(self, double speed):
		self.speed = speed
		self.xf1, self.xf2 = self._xfade(speed)

	cdef _xfade(self, double speed):
		if speed < 2.0:
			return 1.0, 0.0
		elif speed < 4.0:
			d = (speed - 2.0) / 2.0
			return 1.0 - d, d
		else:
			return 0.0, 1.0

class StepperCluster(object):
	SAMPLERATE = 48000
	PERIODSIZE = 1024
	def __init__(self, soundcard, channels, move):
		cards = alsaaudio.cards()
		if not soundcard in cards:
			print "Error: did not find soundcard named:", soundcard
			raise ValueError
		pcmname = "surround71:CARD=" + soundcard + ",DEV=0"
		self.pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, pcmname)
		self.pcm.setchannels(channels * 2)
		self.pcm.setrate(self.SAMPLERATE)
		self.pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
		self.pcm.setperiodsize(self.PERIODSIZE)
		self.motors = [Stepper(self.SAMPLERATE, self.PERIODSIZE, 30000, 0) for x in range(channels)]
		self.dim = len(self.motors)
		self.packer = struct.Struct("<" + "hh" * channels)
		self.set_home()
		self.set_destination(self.position)
		self.max_speeds = [5.0 for x in range(self.dim)]
		self.position_generator = move.position()
		self.currents = [0.0 for x in range(self.dim * 2)]
		self.data = ""
		self.chompsize = self.PERIODSIZE * self.packer.size
		self.ti = time.time()
		self.set_speed([0.0 for x in range(self.dim)])

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
		self.delta_t = 1.0 # FIXME: Start speed
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
		cdef double dtinc
		cdef double dt
		#spd = self._vec_mul_scalar(self.incvec, self.delta_t)
		#print "Speeds:", repr(spd)
		#self.set_speed(spd)
		ret = self.next_position()
		#print self.delta_t
		dtinc = 0.01
		dt = self.dist - self.time
		if ((self.delta_t - 1.0) / dtinc) >= dt and self.delta_t > 1.0:
			self.delta_t -= dtinc
		elif self.delta_t < (5.0 - dtinc):
			self.delta_t += dtinc
		#if self.delta_t < 4.9:
		#	print self.delta_t
		return ret

	def set_speed(self, speed):
		# assert(len(speed) <= len(self.motors))
		cdef int i
		for i in range(self.dim):
			self.motors[i].set_speed(abs(speed[i]))

	def main_iteration(self):
		cdef int i, n
		if self.time >= self.dist:
			dst = next(self.position_generator, self.position)
			print "New destination:", repr(dst)
			self.set_destination(*dst)
		steps = self.pos_iteration()
		for i in range(self.dim):
			s = steps[i]
			if s:
				vl, vr = self.motors[i].do_step(s)
				self.currents[i * 2] = vl
				self.currents[i * 2 + 1] = vr
		#print repr(self.currents)
		data = self.packer.pack(*self.currents)
		self.data += data * int(15.0 / self.delta_t)
		if len(self.data) >= self.chompsize:
			n = self.pcm.write(self.data[:self.chompsize]) * self.packer.size
			self.data = self.data[n:]

	def main_loop(self):
		while True:
			self.main_iteration()

	def zero_output(self):
		val = [0.0 for x in range(self.dim * 2)]
		data = self.packer.pack(*val) * self.PERIODSIZE
		self.pcm.write(data)
		self.pcm.write(data)
		self.pcm.write(data)
		self.pcm.write(data)
		self.pcm.write(data)
		self.pcm.close()

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

idx = 0
points = [[100, 80, 50, 20], [-10, -100, 50, 20], [-10, 20, 30, 40], [0, 0, 0, 0]]
def position_cb():
	global idx
	global points
	ret = points[idx]
	idx += 1
	if idx >= len(points):
		idx = 0
	return ret

def main_test_pos():
	c = StepperCluster('Device', 4, position_cb)
	c.main_loop()

if __name__ == "__main__":
	main_test_pos()

