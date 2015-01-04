#!/usr/bin/env python3
#
# vim: set tabstop=4:
#
# Copyright (c) 2015 David Jander
#
# Based on code contained in the Python standard library:
# Copyright (c) 2001-2015 Python Software Foundation.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#
# This module does monkey-patching to add EPOLLPRI/EPOLLERR support to the
# asyncio module of python 3.4. Hopefully one day this will go into the
# python-tulip project.
# For this to work, this module needs to be imported before asyncio and/or
# selectors. Ideally this will be the first module imported by any main
# application.
#

import selectors
import select

from selectors import EVENT_READ, EVENT_WRITE
EVENT_EXCEPT = (1 << 2)

selectors.EVENT_EXCEPT = EVENT_EXCEPT

#
# Patch SelectSelector
#

def SelectSelector___init__(self):
	super().__init__()
	self._readers = set()
	self._writers = set()
	self._excepter = set()

def SelectSelector_register(self, fileobj, events, data=None):
	if (not events) or (events & ~(EVENT_READ | EVENT_WRITE | EVENT_EXCEPT)):
		raise ValueError("Invalid events: {!r}".format(events))

	key = selectors.SelectorKey(fileobj, self._fileobj_lookup(fileobj), events, data)

	if key.fd in self._fd_to_key:
		raise KeyError("{!r} (FD {}) is already registered"
				.format(fileobj, key.fd))

	self._fd_to_key[key.fd] = key
	if events & EVENT_READ:
		self._readers.add(key.fd)
	if events & EVENT_WRITE:
		self._writers.add(key.fd)
	if events & EVENT_EXCEPT:
		self._excepter.add(key.fd)
	return key

def SelectSelector_unregister(self, fileobj):
	key = super().unregister(fileobj)
	self._readers.discard(key.fd)
	self._writers.discard(key.fd)
	self._excepters.discard(key.fd)
	return key

def SelectSelector_select(self, timeout=None):
	timeout = None if timeout is None else max(timeout, 0)
	ready = []
	try:
		r, w, e = self._select(self._readers, self._writers, self._excepters, timeout)
	except InterruptedError:
		return ready
	r = set(r)
	w = set(w)
	e = set(e)
	for fd in r | w | e:
		events = 0
		if fd in r:
			events |= EVENT_READ
		if fd in w:
			events |= EVENT_WRITE
		if fd in e:
			events |= EVENT_EXCEPT

		key = self._key_from_fd(fd)
		if key:
			ready.append((key, events & key.events))
	return ready

selectors.SelectSelector.__init__ = SelectSelector___init__
selectors.SelectSelector.register = SelectSelector_register
selectors.SelectSelector.unregister = SelectSelector_unregister
selectors.SelectSelector.select = SelectSelector_select

#
# Patch PollSelector
#

# TODO!!!

#
# Patch EpollSelector
#

def EpollSelector_register(self, fileobj, events, data=None):
	if (not events) or (events & ~(EVENT_READ | EVENT_WRITE | EVENT_EXCEPT)):
		raise ValueError("Invalid events: {!r}".format(events))

	key = selectors.SelectorKey(fileobj, self._fileobj_lookup(fileobj), events, data)

	if key.fd in self._fd_to_key:
		raise KeyError("{!r} (FD {}) is already registered"
				.format(fileobj, key.fd))

	self._fd_to_key[key.fd] = key
	epoll_events = 0
	if events & EVENT_READ:
		epoll_events |= select.EPOLLIN
	if events & EVENT_WRITE:
		epoll_events |= select.EPOLLOUT
	if events & EVENT_EXCEPT:
		epoll_events |= select.EPOLLPRI | select.EPOLLERR
	self._epoll.register(key.fd, epoll_events)
	return key

def EpollSelector_select(self, timeout=None):
	if timeout is None:
		timeout = -1
	elif timeout <= 0:
		timeout = 0
	else:
		# epoll_wait() has a resolution of 1 millisecond, round away
		# from zero to wait *at least* timeout seconds.
		timeout = math.ceil(timeout * 1e3) * 1e-3

	max_ev = len(self._fd_to_key)
	ready = []
	try:
		fd_event_list = self._epoll.poll(timeout, max_ev)
	except InterruptedError:
		return ready
	for fd, event in fd_event_list:
		events = 0
		if event & select.EPOLLOUT:
			events |= EVENT_WRITE
		if event & select.EPOLLIN:
			events |= EVENT_READ
		if event & (select.EPOLLPRI | select.EPOLLERR):
			events |= EVENT_EXCEPT

		key = self._key_from_fd(fd)
		if key:
			ready.append((key, events & key.events))
	return ready

selectors.EpollSelector.register = EpollSelector_register
selectors.EpollSelector.select = EpollSelector_select

from asyncio import selector_events, events

#
# Patch BaseSelectorEventLoop
#

def BaseSelectorEventLoop_add_reader(self, fd, callback, *args):
	"""Add a reader callback."""
	if self._selector is None:
		raise RuntimeError('Event loop is closed')
	handle = events.Handle(callback, args, self)
	try:
		key = self._selector.get_key(fd)
	except KeyError:
		self._selector.register(fd, selectors.EVENT_READ,
					            (handle, None, None))
	else:
		mask, (reader, writer, excepter) = key.events, key.data
		self._selector.modify(fd, mask | selectors.EVENT_READ,
					          (handle, writer, excepter))
		if reader is not None:
			reader.cancel()

def BaseSelectorEventLoop_remove_reader(self, fd):
	"""Remove a reader callback."""
	if self._selector is None:
		return False
	try:
		key = self._selector.get_key(fd)
	except KeyError:
		return False
	else:
		mask, (reader, writer, excepter) = key.events, key.data
		mask &= ~selectors.EVENT_READ
		if not mask:
			self._selector.unregister(fd)
		else:
			self._selector.modify(fd, mask, (None, writer, excepter))

		if reader is not None:
			reader.cancel()
			return True
		else:
			return False

def BaseSelectorEventLoop_add_writer(self, fd, callback, *args):
	"""Add a writer callback.."""
	if self._selector is None:
		raise RuntimeError('Event loop is closed')
	handle = events.Handle(callback, args, self)
	try:
		key = self._selector.get_key(fd)
	except KeyError:
		self._selector.register(fd, selectors.EVENT_WRITE,
					            (None, handle, None))
	else:
		mask, (reader, writer, excepter) = key.events, key.data
		self._selector.modify(fd, mask | selectors.EVENT_WRITE,
					          (reader, handle, excepter))
		if writer is not None:
			writer.cancel()

def BaseSelectorEventLoop_remove_writer(self, fd):
	"""Remove a writer callback."""
	if self._selector is None:
		return False
	try:
		key = self._selector.get_key(fd)
	except KeyError:
		return False
	else:
		mask, (reader, writer, excepter) = key.events, key.data
		# Remove both writer and connector.
		mask &= ~selectors.EVENT_WRITE
		if not mask:
			self._selector.unregister(fd)
		else:
			self._selector.modify(fd, mask, (reader, None, excepter))

		if writer is not None:
			writer.cancel()
			return True
		else:
			return False

def BaseSelectorEventLoop_add_excepter(self, fd, callback, *args):
	"""Add an excepter callback."""
	if self._selector is None:
		raise RuntimeError('Event loop is closed')
	handle = events.Handle(callback, args, self)
	try:
		key = self._selector.get_key(fd)
	except KeyError:
		self._selector.register(fd, selectors.EVENT_EXCEPT,
					            (None, None, handle))
	else:
		mask, (reader, writer, excepter) = key.events, key.data
		self._selector.modify(fd, mask | selectors.EVENT_EXCEPT,
					          (reader, writer, handle))
		if excepter is not None:
			excepter.cancel()

def BaseSelectorEventLoop_remove_excepter(self, fd):
	"""Remove an excepter callback."""
	if self._selector is None:
		return False
	try:
		key = self._selector.get_key(fd)
	except KeyError:
		return False
	else:
		mask, (reader, writer, excepter) = key.events, key.data
		mask &= ~selectors.EVENT_EXCEPT
		if not mask:
			self._selector.unregister(fd)
		else:
			self._selector.modify(fd, mask, (reader, writer, None))

		if excepter is not None:
			excepter.cancel()
			return True
		else:
			return False

def BaseSelectorEventLoop__process_events(self, event_list):
	for key, mask in event_list:
		fileobj, (reader, writer, excepter) = key.fileobj, key.data
		if mask & selectors.EVENT_READ and reader is not None:
			if reader._cancelled:
				self.remove_reader(fileobj)
			else:
				self._add_callback(reader)
		if mask & selectors.EVENT_WRITE and writer is not None:
			if writer._cancelled:
				self.remove_writer(fileobj)
			else:
				self._add_callback(writer)
		if mask & selectors.EVENT_EXCEPT and excepter is not None:
			if excepter._cancelled:
				self.remove_excepter(fileobj)
			else:
				self._add_callback(excepter)

selector_events.BaseSelectorEventLoop.add_reader = BaseSelectorEventLoop_add_reader
selector_events.BaseSelectorEventLoop.remove_reader = BaseSelectorEventLoop_remove_reader
selector_events.BaseSelectorEventLoop.add_writer = BaseSelectorEventLoop_add_writer
selector_events.BaseSelectorEventLoop.remove_writer = BaseSelectorEventLoop_remove_writer
selector_events.BaseSelectorEventLoop.add_excepter = BaseSelectorEventLoop_add_excepter
selector_events.BaseSelectorEventLoop.remove_excepter = BaseSelectorEventLoop_remove_excepter
selector_events.BaseSelectorEventLoop._process_events = BaseSelectorEventLoop__process_events

