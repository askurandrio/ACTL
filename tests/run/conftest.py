import sys
from multiprocessing import Queue, Process
from queue import Empty

import pytest

from actl.run import main, parseArgs


class _AbstractIoQueue:
	def __init__(self):
		self._queue = Queue()
		self._process = None

	def bind(self, process):
		self._process = process

	def _get(self, timeout):
		for _ in range(timeout * 2):
			try:
				return self._queue.get(timeout=0.5)
			except Empty:
				if (self._process is None) or (not self._process.is_alive()):
					raise

		raise Empty

	def readAll(self):
		def gen():
			while self:
				yield self._queue.get_nowait()

		return list(gen())

	def __bool__(self):
		return not self._queue.empty()


class _WriteIoQueue(_AbstractIoQueue):
	def write(self, content):
		self._queue.put(content)

	def get(self):
		return self._get(timeout=5)


class _ReadIoQueue(_AbstractIoQueue):
	def put(self, line):
		self._queue.put(line)

	def readline(self):
		return self._get(timeout=5)


class _Run:
	def __init__(self):
		self._process = None
		self._stdin = _ReadIoQueue()
		self._stdout = _WriteIoQueue()

	def _target(self, args):
		sys.stdin = self._stdin
		sys.stdout = self._stdout
		main(**parseArgs(list(args)))

	def __enter__(self):
		def run_(*args):
			self._process = Process(target=self._target, args=(args,))
			self._process.start()
			self._stdin.bind(self._process)
			self._stdout.bind(self._process)

		run_.stdin = self._stdin
		run_.stdout = self._stdout

		return run_

	def __exit__(self, *_):
		self._process.join(timeout=5)
		assert not self._stdin, self._stdin.readAll()
		assert not self._stdout, self._stdout.readAll()
		try:
			assert not self._process.is_alive()
		except AssertionError:
			self._process.terminate()
			raise


@pytest.fixture
def run():
	with _Run() as run_:
		yield run_
