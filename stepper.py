#
# Copyright (c) 2014 David Jander
#
# vim: set tabstop=4:
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import monkeypatch
import asyncio
from audiostep import audiostep
from gpio import AsyncGPInput

class StepperCluster(object):
	def __init__(self, audiodev, dim, cfg):
		self.cfg = cfg
		self.invert = [1 - int(x) * 2 for x in cfg.settings["invert_motor"]]
		self.audio = audiostep(audiodev, dim)
		cfb = self.cfg.settings["current_feedback"]
		if cfb:
			self.audio.set_amplitude_dc(1.0)
		else:
			self.audio.set_amplitude_dc(0.3)
		self.dim = dim
		self.prepare_endswitches()
		self.set_speed_scale(1.0)
		self.max_feedrate = cfg.settings["max_feedrate"] / 60.0

	def set_speed_scale(self, ss):
		self.speed_scale = ss

	def set_max_feedrate(self, limit):
		if limit:
			self.max_feedrate = limit

	def prepare_endswitches(self):
		self.esw = []
		for axis in ["X", "Y", "Z"]:
			eswname = "endstop_" + axis
			self.esw.append(AsyncGPInput(eswname, self))

	def gpio_event(self, name, val):
		print("GPIO Event from", name, "value:", val)
		self.stop()
		self.cancel_destination()
		self.restart()

	def handle_command(self, obj):
		cmd = obj[0]
		pos = obj[1]
		if cmd == "feedrate":
			rate = pos
			#print "Feedrate:", pos, "rate =", rate
			self.set_feedrate(rate)
		elif cmd == "position":
			#print "Position:", repr(pos)
			self.set_destination(pos)
		elif cmd == "sethome":
			print("Setting home pos:", repr(pos))
			if pos is None:
				self.audio.set_home()
			else:
				self.audio.set_position(pos)
		else:
			print("SC: Unknown object:", repr(obj))

	def set_feedrate(self, rate):
		rate = self.speed_scale * rate
		if self.max_feedrate and rate > self.max_feedrate:
			rate = self.max_feedrate
		high = rate / 600.0
		low = high
		if low > 0.05:
			low = 0.05
		self.audio.set_feedrate(low, high, low)

	def set_destination(self, pos):
		current = self.audio.get_position()
		for i, sw in enumerate(self.esw):
			inp = sw.read_value()
			if not inp and current[i] > pos[i] * self.invert[i]:
				pos[i] = current[i]
		self.audio.set_destination(pos)

	def process_one_move(self):
		self.audio.process_one_move()

	def zero_output(self):
		self.audio.zero_output()

	def close(self):
		self.audio.close()

	def stop(self):
		self.audio.stop()

	def restart(self):
		self.audio.restart()

	def cancel_destination(self):
		self.audio.cancel_destination()

	def fileno(self):
		return self.audio.fileno()

	def write_more(self):
		return self.audio.write_more()

	def main_loop(self):
		while True:
			if not self.main_iteration():
				break
		self.zero_output()
		self.close()
