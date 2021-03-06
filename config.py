#
# vim: set tabstop=4:
#
# Copyright (c) 2014 David Jander
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

from math import *
import sys
import configparser

class Config(object):
	def __init__(self, cfgfilename):
		defaults = {
			"num_motors" : "4",
			"motor_name" : "['X', 'Y', 'Z', 'E']",
			"max_feedrate" : "5000",
			"steps_per_mm" : "[80, 80, 4260, 670]",
			"invert_motor" : "[True, False, False, True]",
			"current_feedback" : 'False',
			"print_volume" : "[200, 200, 200]",
			"sound_device" : "'Device'",
			"sound_rate" : "48000",
			"hwmon_device" : "'hwmon0'",
			"temp_bed_sensor" : "'in7_input'",
			"temp_ext_sensor" : "'in6_input'",
			"temp_bed_scale" : "10.0 / (1 + 1.0/1.2)",
			"temp_ext_scale" : "10.0 / (1 + 1.0/1.2)",
			"temp_bed_offset" : "-0.005",
			"temp_ext_offset" : "-0.005",
		}
		self.config = configparser.SafeConfigParser(defaults)
		self.config.read([cfgfilename])
		# self.config.write(sys.stdout)
		self.settings = self.config.defaults()
		for s in self.settings:
			self.settings[s] = eval(self.settings[s])
