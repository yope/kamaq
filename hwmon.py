#!/usr/bin/env python
#
# vim: set tabstop=4:
#
# Copyright (c) 2014 David Jander
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import os

HWMON_SYSFS_PATH = "/sys/class/hwmon/"

class HWmonSensor(object):
	def __init__(self, cfg, name):
		self.hwmonpath = os.path.join(os.path.join(HWMON_SYSFS_PATH,
				cfg.settings["hwmon_device"]), "device")
		self.hwmonname = os.path.join(self.hwmonpath, name)

	def read(self):
		f = open(self.hwmonname, "r")
		txt = f.read().strip(" \r\n")
		f.close()
		return float(txt) / 1000.0

class ScaledSensor(object):
	def __init__(self, cfg, channel):
		cfgname = "temp_" + channel.lower() + "_"
		name = cfg.settings[cfgname + "sensor"]
		self.scale = cfg.settings[cfgname + "scale"]
		self.offset = cfg.settings[cfgname + "offset"]
		self.hwmon = HWmonSensor(cfg, name)

	def read(self):
		x = self.hwmon.read()
		return x * self.scale + self.offset

# Test function
if __name__ == "__main__":
	from config import Config
	s = ScaledSensor(Config("grunner.conf"), "EXT")
	print(repr(s.read()))

