#!/usr/bin/env python
#
# vim: set tabstop=4:

from math import *
import sys

class GCode(object):
	def __init__(self, cfg, filename):
		self.f = open(filename, "r")
		self.dim = cfg.settings["num_motors"]
		self.motor_name = cfg.settings["motor_name"]
		self.position = self.position_generator()
		self.pos = [0.0 for x in range(self.dim)]

	def process_M(self, code, args):
		print "Process M: code =", code, repr(args)

	def process_G(self, code, args):
		if code == 1:
			for w in args:
				if w == ";":
					return self.pos
				if len(w) < 2:
					continue
				mn = w[0]
				try:
					val = float(w[1:])
				except ValueError:
					continue
				if mn in self.motor_name:
					idx = self.motor_name.index(mn)
					self.pos[idx] = val
				else:
					print "G1 unknown code:", w
			return self.pos
		else:
			print "Unimplemented G: code =", code, repr(args)
		return None

	def process_T(self, code, args):
		print "Process T: code =", code, repr(args)

	def process_line(self, cmd, l):
		words = l.split()
		try:
			code = int(words[0], 10)
		except ValueError:
			return None
		words = words[1:]
		if cmd == "G":
			return self.process_G(code, words)
		elif cmd == "M":
			return self.process_M(code, words)
		elif cmd == "T":
			return self.process_T(code, words)

	def position_generator(self):
		for l in self.f:
			cmd = l[0]
			if not cmd in ['G', 'M', 'T']:
				continue
			ret = self.process_line(cmd, l[1:].strip(" \r\n"))
			if ret is not None:
				yield ret
		f.close()
		raise StopIteration

if __name__ == "__main__":
	cfg = Config("bla.ini")
	g = GCode(cfg, sys.argv[1])

