#!/usr/bin/env python
#
# vim: set tabstop=4:

from math import *
from gcode import GCode
import signal
import sys

class Move(object):
	def __init__(self, cfg, gcode):
		self.mm2steps = [float(x) for x in cfg.settings["steps_per_mm"]]
		self.dim = cfg.settings["num_motors"]
		self.motor_name = cfg.settings["motor_name"]
		self.plist = [[100, 80, 50, 20], [-10, -100, 50, 20], [-10, 20, 30, 40], [0, 0, 0, 0]]
		self.gcode = gcode

	def transform(self, gpos):
		ret = map(lambda x, y: x * y, gpos, self.mm2steps)
		return ret

	def position(self):
		#while True:
		#	for p in self.plist:
		#		yield self.transform(p)
		while True:
			try:
				gpos = next(self.gcode.position)
			except StopIteration:
				break
			p = self.transform(gpos)
			yield p

if __name__ == "__main__":
	from config import Config
	from stepper import StepperCluster

	cfg = Config("bla.cfg")
	g = GCode(cfg, "enchufe.gcode")
	m = Move(cfg, g)
	n = cfg.settings["num_motors"]
	snd = cfg.settings["sound_device"]
	sc = StepperCluster(snd, n, m)
	def signal_handler(signal, frame):
		print('You pressed Ctrl+C!')
		sc.zero_output()
		sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)
	sc.main_loop()

