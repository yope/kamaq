#!/usr/bin/env python3
#
# vim: set tabstop=4:
#
# Copyright (c) 2014 David Jander
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import monkeypatch
from config import Config
from printer import Printer
from webui import WebUi
import sys
import signal

class Kamaq(object):
	def __init__(self, argv):
		self.sc = None
		self.cfg = Config("kamaq.conf")
		self.run_webui()

	def shutdown(self):
		self.printer.shutdown()
		sys.exit(0)

	def run_webui(self):
		signal.signal(signal.SIGINT, self.signal_handler)
		self.printer = Printer(self.cfg)
		self.webui = WebUi(self.printer)
		self.printer.add_webui(self.webui)
		self.printer.run()

	def signal_handler(self, signal, frame):
		print('You pressed Ctrl+C!')
		if not hasattr(self, "printer"):
			return # Ignore....
		self.shutdown()

if __name__ == "__main__":
	k = Kamaq(sys.argv[1:])

