#!/usr/bin/env python3
#
# vim: set tabstop=4:
#
# Copyright (c) 2014 David Jander
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

from config import Config
from audiostep import audiostep
import sys

cfg = Config("grunner.conf")
dim = cfg.settings["num_motors"]
vec = [0.0 for x in range(dim * 2)]
if len(sys.argv) > 1:
	for i in range(len(sys.argv) - 1):
		vec[i] = float(sys.argv[i + 1])
audiodev = cfg.settings["sound_device"]
audio = audiostep(audiodev, dim)
while True:
	audio.set_constant_current(vec)
audio.zero_output()
audio.close()

