#!/usr/bin/env python
#
# vim: set tabstop=4:
#
# Copyright (c) 2015 David Jander
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

from temp100k import Thermistor100k
from hwmon import ScaledSensor
from gpio import GPOutput
from pid import PidController
from gcode import GCode
from move import Move
import time
import asyncio
import queue

class AIOFileReader(object):
	def __init__(self, fname, queue=None):
		if queue is None:
			self.queue = queue.Queue(10)
		else:
			self.queue = queue
		self.loop = asyncio.get_event_loop()
		self.fname = fname
		self.eof = False
		self.loop.run_in_executor(None, self.read_thread)

	def read_thread(self):
		with open(self.fname, "r") as f:
			for l in f:
				self.queue.put(l)
		self.eof = True

	def readline(self):
		try:
			ret = self.queue.get_nowait()
		except queue.Empty:
			if self.eof:
				ret = None
			else:
				ret = ""
		return ret

	def eof(self):
		return self.eof and self.queue.empty()

class Printer(object):
	def __init__(self, cfg, sc):
		self.cfg = cfg
		self.webui = None
		self.gcode_queue = queue.Queue(100)
		self.gcode_file = None
		self.command_queue = asyncio.Queue(100)
		self.idling = True
		self.pid = {}
		self.setpoint = {}
		self.move = Move(self.cfg, self)
		self.gcode = GCode(self.cfg)
		self.sc = sc
		self.current_e = 0
		self.extruder_safety_timeout = 300 # FIXME
		self.extruder_safety_time = time.time() + self.extruder_safety_timeout
		for n in ["ext", "bed"]:
			name = n.upper()
			o = GPOutput("heater_" + name)
			s = ScaledSensor(self.cfg, name)
			t = Thermistor100k(s)
			self.pid[n] = PidController(t, o, 0.3, 0.004, 0.5)
		self.loop = asyncio.get_event_loop()
		self.loop.add_writer(self.sc.fileno(), self.handle_sc_write)
		asyncio.async(self.gcode_processor())

	def add_webui(self, webui):
		self.webui = webui

	def launch_pid(self, name, sp):
		self.pid[name].spawn()
		self.set_setpoint(name, sp)

	def shutdown(self):
		for name in self.pid:
			self.pid[name].set_setpoint(0)
			self.pid[name].shutdown()

	def set_setpoint(self, name, sp):
		self.setpoint[name] = sp
		self.pid[name].set_setpoint(sp)

	def get_temperature(self, name):
		return self.pid[name].get_input()

	def set_position_mm(self, x, y, z, e):
		if self.webui:
			self.webui.queue_move(x, y, z, e)
		if e != self.current_e:
			self.current_e = e
			self.extruder_safety_time = time.time() + self.extruder_safety_timeout

	def printer_handler(self):
		ti = time.time()
		if self.extruder_safety_time < ti and "ext" in self.pid and \
				self.setpoint["ext"] > 150:
			print("Extruder safety timeout hit. Lowering setpoint!")
			self.pid["ext"].set_setpoint(self.setpoint["ext"] - 50)

	@asyncio.coroutine
	def print_file(self, fname):
		if self.gcode_file is not None:
			return False
		print("Starting print:", fname)
		self.gcode_file = AIOFileReader(fname, self.gcode_queue)
		asyncio.sleep(0)
		return True

	@asyncio.coroutine
	def execute_gcode(self, cmd):
		try:
			self.gcode_queue.put_nowait(cmd)
		except queue.Full:
			return False
		yield from asyncio.sleep(0)
		return True

	def _read_gcode(self):
		try:
			ret = self.gcode_queue.get_nowait()
		except queue.Empty:
			ret = ""
		return ret

	@asyncio.coroutine
	def gcode_processor(self):
		while True:
			if self.gcode_file is None and self.gcode_queue.empty():
				yield from asyncio.sleep(0.2)
				continue
			if self.gcode_file:
				l = self.gcode_file.readline()
			else:
				l = self._read_gcode()
			if l is None: # End of file
				self.gcode_file = None
				continue
			elif len(l) == 0: # File reader stalled
				yield from asyncio.sleep(0)
				continue
			obj = self.gcode.process_line(l)
			if obj is None:
				continue
			# print("Move:", repr(obj))
			yield from self.move.process_command(obj, self.command_queue)

	def update_status(self):
		if self.idling:
			status = "idle"
		elif self.gcode_file is not None:
			status = "processing"
		else:
			status = "moving"
		ext = "off" # FIXME
		bed = "off" # FIXME
		self.webui.queue_status(status, ext, bed)

	def set_idle(self, idle):
		if idle != self.idling:
			self.idling = idle
			self.update_status()

	def handle_sc_write(self):
		if not self.idling:
			ret = self.sc.write_more()
		else:
			ret = None
		while ret is None:
			try:
				pos = self.command_queue.get_nowait()
			except asyncio.QueueEmpty:
				self.sc.zero_output()
				self.set_idle(True)
				break
			self.sc.handle_command(pos)
			ret = self.sc.write_more()
			self.set_idle(False)

	def run(self):
		self.loop.run_forever()
