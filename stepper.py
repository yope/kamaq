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
import asyncore

class StepperCluster(object):
	def __init__(self, audiodev, dim, cfg, move):
		self.move = move
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
		self.speed_scale = 1.0
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

	def get_next_destination(self):
		if self.move is None:
			return None
		try:
			obj = next(self.move.movements)
		except StopIteration:
			return False
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
			print("Setting home pos:", repr(self.audio.get_position()))
			self.audio.set_home()
		else:
			print("SC: Unknown object:", repr(obj))
		return True

	def main_iteration(self):
		ret = self.get_next_destination()
		if ret:
			self.process_one_move()
		return ret

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

class StepperClusterDispatcher(asyncore.file_dispatcher):
	def __init__(self, stepper_cluster, callback):
		self.sc = stepper_cluster
		self.cb = callback
		asyncore.file_dispatcher.__init__(self, self.sc.fileno())

	def writable(self):
		return True

	def readable(self):
		return False

	def exceptable(self):
		return False

	def handle_write(self):
		ret = self.sc.write_more()
		while ret is None:
			ret = self.sc.get_next_destination()
			if ret is None:
				break
			if ret:
				ret = self.sc.write_more()
		if not ret:
			self.cb.end_of_file()
