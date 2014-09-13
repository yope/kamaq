#
# Copyright (c) 2014 David Jander
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# vim: set tabstop=4:

from audiostep import audiostep
import asyncore

class StepperCluster(object):
	def __init__(self, audiodev, dim, cfg, move):
		self.move = move
		self.cfg = cfg
		self.audio = audiostep(audiodev, dim)
		self.dim = dim

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
		else:
			print "SC: Unknown object:", repr(obj)
		return True

	def main_iteration(self):
		ret = self.get_next_destination()
		if ret:
			self.process_one_move()
		return ret

	def set_feedrate(self, rate):
		self.audio.set_feedrate(rate / 600.0)

	def set_destination(self, pos):
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
		if ret is None:
			self.cb.end_of_file()
