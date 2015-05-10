#
# Copyright (c) 2014 David Jander
#
# vim: set tabstop=4:
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

from audiostep import audiostep
from gpio import AsyncGPInput

class StepperCluster(object):
	def __init__(self, audiodev, dim, cfg, esw):
		self.cfg = cfg
		self.invert = [1 - int(x) * 2 for x in cfg.settings["invert_motor"]]
		self.audio = audiostep(cfg, audiodev, dim, esw)
		cfb = self.cfg.settings["current_feedback"]
		if cfb:
			self.audio.set_amplitude_dc(1.0)
		else:
			self.audio.set_amplitude_dc(0.3)
		self.dim = dim
		self.set_speed_scale(1.0)
		self.set_max_feedrate(cfg.settings["max_feedrate"] / 60.0)

	def connect_cmd_buffer(self, buf):
		self.audio.connect_cmd_buffer(buf)

	def pull_cmd_buffer(self):
		return self.audio.pull_cmd_buffer()

	def set_speed_scale(self, ss):
		self.speed_scale = ss
		self.audio.set_speed_scale(ss)

	def set_max_feedrate(self, limit):
		if limit:
			self.max_feedrate = limit
		self.audio.set_max_feedrate(limit)

	def handle_command(self, obj):
		cmd = obj[0]
		pos = obj[1]
		if cmd == "feedrate":
			rate = pos
			self.set_feedrate(rate)
		elif cmd == "feedrate3":
			rate = pos
			self.set_feedrate3(*rate)
		elif cmd == "position":
			self.set_destination(pos)
		elif cmd == "set_position":
			print("Setting pos:", repr(pos))
			if pos is None:
				self.audio.set_home()
			else:
				self.audio.set_position(pos)
		else:
			print("SC: Unknown object:", repr(obj))

	def set_feedrate(self, rate):
		self.audio.set_feedrate(rate, rate, rate)

	def set_feedrate3(self, begin, high, end):
		self.audio.set_feedrate(begin, high, end)

	def set_destination(self, pos):
		self.audio.set_destination(pos)

	def get_position(self):
		return self.audio.get_position()

	def set_position(self, pos):
		self.audio.set_position(pos)

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
