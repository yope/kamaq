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
		self.pos = {}
		for m in self.motor_name:
			self.pos[m] = 0.0
		self.pos["F"] = 0.0 # Feedrate
		self.pos["command"] = "position" # Default position command
		self.commands = self.command_generator()

	def process_M(self, code, args):
		if code == 82: # Absolute E codes
			pass
		elif code == 104: # Set hotend temperature
			print "Set temperature:", args[0]
		elif code == 106: # Set extruder fan speed
			print "Set extruder fan speed:", args[0]
		else:
			print "Unimplemented M: code =", code, repr(args)

	def process_G(self, code, args):
		if code == 1 or code == 0: # Controlled movement
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
				if mn in self.pos:
					if mn == "F":
						val = val / 60
					self.pos[mn] = val
				else:
					print "G1 unknown code:", w
			return self.pos
		elif code == 21: # Set metric units
			pass
		elif code == 28: # Home position
			print "Home position"
			# TODO: Implement homing
		elif code == 90: # Absolute positioning
			pass
		elif code == 92: # Set home
			# TODO: Implement home offsetting
			pass
		else:
			print "Unimplemented G: code =", code, repr(args)
		return None

	def process_T(self, code, args):
		if code == 0: # Tool selection 0
			pass
		else:
			print "Unimplemented T: code =", code, repr(args)

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

	def command_generator(self):
		for l in self.f:
			cmd = l[0]
			if not cmd in ['G', 'M', 'T']:
				continue
			ret = self.process_line(cmd, l[1:].strip(" \r\n"))
			if ret is not None:
				yield ret
		self.f.close()
		raise StopIteration

if __name__ == "__main__":
	cfg = Config("bla.ini")
	g = GCode(cfg, sys.argv[1])

