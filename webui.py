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

# Add external modules paths to sys.path...
import os
import sys
pwd = os.getcwd()
sys.path.append(os.path.join(pwd, "aiohttp"))
sys.path.append(os.path.join(pwd, "websockets"))

import monkeypatch
import asyncio
from aiohttp import web
import websockets
import json
from collections import deque

import random
random.seed()

class WsHanlder(object):
	def __init__(self, websock, webui):
		self.webui = webui
		self.ws_acked = True
		self.ws_queue = []
		self.websock = websock
		self.webui.add_websocket(self)
		self.queue = deque()

	@asyncio.coroutine
	def send_message(self, obj):
		txt = json.dumps(obj)
		yield from self.websock.send(txt)

	@asyncio.coroutine
	def coro_queue(self):
		while self.queue:
			obj = self.queue.popleft()
			yield from self.send_message(obj)

	def queue_message(self, obj):
		start = not self.queue
		self.queue.append(obj)
		if start:
			asyncio.async(self.coro_queue())

	@asyncio.coroutine
	def coro_recieve(self):
		while True:
			msg = yield from self.websock.recv()
			if msg is None:
				break
			yield from self.on_message(msg)
		self.on_disconnect()

	@asyncio.coroutine
	def on_message(self, message):
		if isinstance(message, bytes):
			message = message.decode('iso8859-1')
		try:
			obj = json.loads(message)
		except ValueError:
			# Garbage or nothing received, close the connection.
			self.on_disconnect()
			self.websock.close()
		else:
			yield from self.parse_object(obj)

	@asyncio.coroutine
	def parse_object(self, obj):
		print("WS: received:", repr(obj))

	def on_disconnect(self):
		print("WS: disconnect")
		self.webui.del_websocket(self)

class WebUi(object):
	def __init__(self, printer):
		print("Starting web server...")
		self.printer = printer
		self.httpd = web.Application()
		self.httpd.router.add_static('/', './html/')
		self.loop = asyncio.get_event_loop()
		f = self.loop.create_server(self.httpd.make_handler(), '0.0.0.0', 8888)
		self.server = self.loop.run_until_complete(f)
		self.wsockets = []
		start = websockets.serve(self.websocket_handler, '0.0.0.0', 9999)
		self.websockd = self.loop.run_until_complete(start)
		print("...done")
		#asyncio.async(self.sim_status())
		#asyncio.async(self.simulate())
		asyncio.async(self.coro_status())

	@asyncio.coroutine
	def websocket_handler(self, websock, path):
		h = WsHanlder(websock, self)
		yield from h.coro_recieve()

	@asyncio.coroutine
	def simulate(self):
		x, y, z = 0, 0, 0
		while True:
			yield from asyncio.sleep(random.randrange(20, 200)/1000.0)
			x += random.randrange(-30, 30)
			y += random.randrange(-30, 30)
			if x > 195: x = 195
			if x < 0: x = 0
			if y > 185: y = 185
			if y < 0: y = 0
			if random.randrange(100) > 97:
				z += 0.2
			if z > 20.0: z = 0
			self.queue_move(x, y, z, 0)

	@asyncio.coroutine
	def coro_status(self):
		while True:
			yield from asyncio.sleep(1)
			t_ext = self.printer.get_temperature("ext")
			t_bed = self.printer.get_temperature("bed")
			self.queue({"id": "status", "temp_ext": t_ext, "temp_bed": t_bed})

	@asyncio.coroutine
	def sim_status(self):
		while True:
			yield from asyncio.sleep(1)
			t_ext = random.randrange(20, 50)
			t_bed = random.randrange(20, 50)
			self.queue({"id": "status", "temp_ext": t_ext, "temp_bed": t_bed})

	def add_websocket(self, wsock):
		print("add_websocket")
		self.wsockets.append(wsock)

	def del_websocket(self, wsock):
		try:
			self.wsockets.remove(wsock)
		except ValueError:
			pass

	@asyncio.coroutine
	def send(self, obj):
		for ws in self.wsockets:
			yield from ws.send_message(obj)

	def queue(self, obj):
		for ws in self.wsockets:
			ws.queue_message(obj)

	def queue_move(self, x, y, z, e):
		self.queue({"id": "move", "x": x, "y": y, "z": z, "e": e})

# Test function
if __name__ == "__main__":
	w = WebUi()
	asyncio.get_event_loop().run_forever()
