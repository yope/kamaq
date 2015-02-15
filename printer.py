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
from vector import Interpolator
import time
import asyncio
import queue

class AIOFileReader(object):
	def __init__(self, fname, fqueue=None):
		if fqueue is None:
			self.queue = queue.Queue(100)
		else:
			self.queue = fqueue
		self.loop = asyncio.get_event_loop()
		self.fname = fname
		self.eof = False
		self.abort = False
		self.loop.run_in_executor(None, self.read_thread)

	def read_thread(self):
		try:
			f = open(self.fname, "r")
		except OSError:
			# FIXME: Signal file not found errors to user...
			self.eof = True
			return
		for l in f:
			self.queue.put(l)
			if self.abort:
				break
		f.close()
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

	def close(self):
		self.abort = True

	def eof(self):
		return self.eof and self.queue.empty()

class Printer(object):
	def __init__(self, cfg, sc):
		self.cfg = cfg
		self.webui = None
		self.gcode_queue = queue.Queue(100)
		self.gcode_file = None
		self.command_queue = asyncio.Queue(5)
		self.idling = True
		self.pause = False
		self.pid = {}
		self.setpoint = {}
		self.setpoint_fail_time = {}
		self.tolerance = 3
		self.current_status = None
		self.heater_enable_mcodes = False
		self.heater_disable_eof = False
		self.machine_ready = False
		self.move = Move(self.cfg, self)
		self.gcode = GCode(self.cfg)
		self.inter = Interpolator(self.cfg)
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
			self.launch_pid(n, 20)
		self.loop = asyncio.get_event_loop()
		self.loop.add_writer(self.sc.fileno(), self.handle_sc_write)
		asyncio.async(self.gcode_processor())
		asyncio.async(self.coro_check_machine())

	def add_webui(self, webui):
		self.webui = webui

	def launch_pid(self, name, sp):
		self.pid[name].spawn()
		self.set_setpoint(name, sp)

	def shutdown(self):
		for name in self.pid:
			self.pid[name].set_setpoint(0)
			self.pid[name].shutdown()

	def set_setpoint(self, name, sp, report=True):
		if sp and sp < 10:
			sp = 10
		elif name == "ext" and sp > 280:
			sp = 280
		elif name == "bed" and sp > 120:
			sp = 120
		print("Set", name, "temperature:", sp, "deg. C")
		self.setpoint[name] = sp
		self.setpoint_fail_time[name] = 0
		self.pid[name].set_setpoint(sp)
		if report and self.webui:
			self.webui.queue_setpoint(name, sp)

	def get_temperature(self, name):
		return self.pid[name].get_input()

	def check_setpoint(self, name):
		temp = self.get_temperature(name)
		sp = self.setpoint[name]
		dt = abs(temp - sp)
		if sp < 30: # Heater off = ok
			dt = 0
		ok = (dt < self.tolerance)
		if ok:
			self.setpoint_fail_time[name] = 0
		elif not self.setpoint_fail_time[name]:
			self.setpoint_fail_time[name] = time.time() + 10
		return (ok or time.time() < self.setpoint_fail_time[name])

	def check_setpoints(self):
		return self.check_setpoint("ext") and self.check_setpoint("bed")

	@asyncio.coroutine
	def coro_check_machine(self):
		self.tolerance = 3
		wasok = True
		while True:
			res = self.check_setpoints()
			if res: # Hysteresis
				self.tolerance = 10
			else:
				self.tolerance = 3
			if not res and wasok:
				print("Printer not ready")
			elif res and not wasok:
				print("Printer ready")
			wasok = res
			self.machine_ready = res
			self.update_status()
			yield from asyncio.sleep(2.0)

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
		self.gcode_file = AIOFileReader(fname)
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
			if (self.gcode_file is None or self.pause) and self.gcode_queue.empty():
				if self.inter.pending():
					yield from self.command_queue.put(("eof", None))
				yield from asyncio.sleep(0.2)
				continue
			if self.gcode_file and not self.pause:
				if not self.machine_ready:
					yield from asyncio.sleep(0.2)
					continue
				l = self.gcode_file.readline()
				if l is None: # End of file
					self.gcode_file = None
					if self.heater_disable_eof:
						self.set_setpoint("ext", 0)
						self.set_setpoint("bed", 0)
					yield from self.command_queue.put(("eof", None))
					continue
			else:
				l = self._read_gcode()
			if len(l) == 0: # File reader stalled
				yield from self.command_queue.put(("eof", None))
				continue
			obj = self.gcode.process_line(l)
			if obj is None:
				continue
			# print("Move:", repr(obj))
			cmd = obj["command"]
			if cmd == "setpoint":
				if self.heater_enable_mcodes:
					self.set_setpoint(obj["type"], obj["value"])
			elif cmd == "log":
				self.webui.queue_log(obj['type'], obj['value'])
			else:
				yield from self.move.process_command(obj, self.command_queue)

	def _heater_status(self, name):
		ok = self.check_setpoint(name)
		sp = self.setpoint[name]
		temp = self.get_temperature(name)
		if sp == 0:
			return "off"
		if ok:
			return "ok"
		if sp > temp:
			return "low"
		if sp < temp:
			return "high"

	def update_status(self, force=False):
		if self.idling:
			motors = "idle"
		elif self.gcode_file is not None:
			motors = "processing"
		else:
			motors = "moving"
		ext = self._heater_status("ext")
		bed = self._heater_status("bed")
		status = (motors, ext, bed)
		if self.webui is None:
			return
		if self.current_status == status:
			return
		self.current_status = status
		self.webui.queue_status(*status)

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
			more = True
			while more and ret is None:
				posout, more = self.inter.process_one(pos)
				pos = None
				if posout is not None:
					self.sc.handle_command(posout)
					ret = self.sc.write_more()
					self.set_idle(False)

	def set_pause(self, pause):
		self.pause = pause
		print("Set pause:", repr(pause))

	@asyncio.coroutine
	def stop(self):
		print("Stopping...")
		if self.gcode_file:
			self.gcode_file.close()
			self.gcode_file = None
		while not self.gcode_queue.empty():
			self.gcode_queue.get_nowait()
		while not self.command_queue.empty():
			self.command_queue.get_nowait()
		self.sc.cancel_destination()
		self.set_setpoint("ext", 0)
		self.set_setpoint("bed", 0)
		yield from self.execute_gcode("G91")
		yield from self.execute_gcode("G1 Z5 F5000")
		yield from self.execute_gcode("G90")

	def set_heater_enable_mcodes(self, value):
		self.heater_enable_mcodes = value

	def set_heater_disable_eof(self, value):
		self.heater_disable_eof = value

	def run(self):
		self.loop.run_forever()
