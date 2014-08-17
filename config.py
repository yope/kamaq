#!/usr/bin/env python
#
# vim: set tabstop=4:

from math import *
import sys
import ConfigParser

class Config(object):
	def __init__(self, cfgfilename):
		defaults = {
			"num_motors" : 4,
			"motor_name" : ['X', 'Y', 'Z', 'E'],
			"max_speed" : [200, 200, 200, 200],
			"steps_per_mm" : [80, 80, 2560, 80],
			"sound_device" : "Device",
			"sound_rate" : 48000,
		}
		self.config = ConfigParser.SafeConfigParser(defaults)
		self.config.read([cfgfilename])
		self.config.write(sys.stdout)
		self.settings = self.config.defaults()

if __name__ == "__main__":
	c = Config("bla.ini")

