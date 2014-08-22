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

