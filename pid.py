#!/usr/bin/env python
#
# vim: set tabstop=4:
#
# Copyright (c) 2014 David Jander
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import time
import multiprocessing
import Queue

def PidProcess(pid, cmdqueue):
	cmd = ""
	print "PID: Starting", pid.actuator.name, "..."
	while True:
		while not cmdqueue.empty():
			try:
				obj = cmdqueue.get()
			except Queue.Empty:
				break
			if not "command" in obj:
				print "PID: Unknown command object:", repr(obj)
				continue
			cmd = obj["command"]
			if cmd == "setpoint":
				pid.set_setpoint(obj["value"])
			elif cmd == "shutdown":
				break
			else:
				print "PID: Unsupported command:", cmd
		if cmd == "shutdown":
			break
		if not pid.iteration():
			break
	print "PID: Shutting down", pid.actuator.name, "..."

class PidController(object):
	def __init__(self, sensor, actuator, P, I, D, period=1.0):
		self.sensor = sensor
		self.actuator = actuator
		self.P = P
		self.I = I * period
		self.D = D / period
		self.integ = 0.0
		self.setpoint = 0
		self.errq = Queue.Queue()
		self.err0 = 0.0
		self.output = 0.0
		self.period = period
		self.windup_limit = 100.0
		self.cmdqueue = multiprocessing.Queue()
		self.outvalue = multiprocessing.Value('d')
		self.proc = multiprocessing.Process(target=PidProcess,
							args=(self, self.cmdqueue))
		self.spawned = False
		self.validate_previous = None

	def set_setpoint(self, sp):
		if self.spawned:
			self.cmdqueue.put({"command": "setpoint", "value": sp})
		else:
			self.setpoint = sp

	def validate_sensor(self, current):
		if current < 10.0:
			print "Temperature too low!"
			return None
		if current > 300.0:
			print "Temperature too high!"
			return None
		prev = self.validate_previous
		if prev is None:
			self.validate_previous = current
			return current
		if abs(prev - current) > 20.0:
			print "Temperature sensor unstable!"
			return None
		self.validate_previous = current
		return current

	def iteration(self):
		current = self.sensor.read()
		current = self.validate_sensor(current)
		if current is None:
			print "Temperature sensor failure detected. Shutting down heater!"
			self.actuator.set_output(0)
			self.outvalue.value = 0
			return False
		err = self.setpoint - current
		derr = err - self.err0
		self.errq.put(err)
		if self.errq.qsize() < 3:
			self.err0 = err
		else:
			self.err0 = self.errq.get()
		self.integ += err
		if self.integ > self.windup_limit:
			self.integ = self.windup_limit
		if self.integ < -self.windup_limit:
			self.integ = -self.windup_limit
		self.output = self.P * err + self.I * self.integ + self.D * derr
		if self.output > 1.0:
			self.output = 1.0
		if self.output < 0.0:
			self.output = 0.0
		ontime = self.output * self.period
		if ontime > 0.0:
			self.actuator.set_output(1)
		time.sleep(ontime)
		if ontime < self.period:
			self.actuator.set_output(0)
			time.sleep(self.period - ontime)
		self.outvalue.value = self.output
		return True

	def get_output(self):
		return self.outvalue.value

	def spawn(self):
		self.proc.start()
		self.spawned = True

	def shutdown(self):
		if not self.spawned:
			return
		self.cmdqueue.put({"command": "shutdown"})
		self.proc.join()
		self.actuator.set_output(0)

if __name__ == "__main__":
	import signal, sys
	from temp100k import Thermistor100k
	from hwmon import ScaledSensor
	from config import Config
	from gpio import GPOutput
	s = ScaledSensor(Config("grunner.conf"), "EXT")
	t = Thermistor100k(s)
	o = GPOutput("heater_EXT")
	p = PidController(t, o, 0.2, 0.002, 0.5)
	def signal_handler(signal, frame):
		print('You pressed Ctrl+C!')
		p.shutdown()
		sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)
	p.spawn()
	sp = 230.0
	p.set_setpoint(sp)
	while True:
		print "Temp =", t.read(), "setpoint =", sp, "Ouput =", p.get_output()
		time.sleep(1.0)
	p.shutdown()

