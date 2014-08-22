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

class StepperCluster(object):
	def __init__(self, audiodev, dim, cfg, move):
		self.move = move
		self.cfg = cfg
		self.audio = audiostep(audiodev, dim)
		self.dim = dim

	def main_iteration(self):
		try:
			obj = next(self.move.movements)
		except StopIteration:
			return False
		cmd = obj[0]
		pos = obj[1]
		if cmd == "feedrate":
			rate = pos / 600.0
			#print "Feedrate:", pos, "rate =", rate
			self.audio.set_feedrate(rate)
		elif cmd == "position":
			#print "Position:", repr(pos)
			self.audio.set_destination(pos)
		else:
			print "SC: Unknown object:", repr(obj)
		self.audio.process_one_move()
		return True

	def zero_output(self):
		self.audio.zero_output()

	def close(self):
		self.audio.close()

	def main_loop(self):
		while True:
			if not self.main_iteration():
				break
		self.zero_output()
		self.close()

