# pylint: disable=redefined-outer-name

import sys
from multiprocessing import Queue, Process

import json
import pytest

import actl
from actl.run import main, parseArgs


class _AbstractIoQueue:
	def __init__(self):
		self._queue = Queue()

	def flush(self):
		pass

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
		return self._queue.get(timeout=5)


class _ReadIoQueue(_AbstractIoQueue):
	def __init__(self):
		self._queue = Queue()

	def put(self, line):
		self._queue.put(line)

	def readline(self):
		return self._queue.get(timeout=5)


def test_CtrlD(run, stdin, stdout):
	run()

	stdin.put('')
	assert stdout.get() == '>>> '


def test_setVar(run, stdin, stdout):
	run()
	assert stdout.get() == '>>> '
	stdin.put('a = 1\n')
	assert stdout.get() == '>>> '
	stdin.put('print(a)\n')
	assert stdout.get() == '1'
	assert stdout.get() == '\n'
	assert stdout.get() == '>>> '
	stdin.put('')


def test_expliciSetProjectF(run, stdin, stdout):
	run('--projectF', 'repl')

	stdin.put('')
	assert stdout.get() == '>>> '


def test_setExtraSource(run, stdin, stdout):
	extraSource = [
		{
			'py-externalKey': {
				'from': 'tests.actl.test_run',
				'import': 'getTestScope',
				'name': 'scope'
			}
		}
	]

	run('--source', json.dumps(extraSource))

	assert stdout.get() == '>>> '
	stdin.put('print(1)\n')
	assert stdout.get() == 'mocked: 1'
	assert stdout.get() == '\n'
	assert stdout.get() == '>>> '
	stdin.put('')


@pytest.fixture
def run(stdin, stdout):
	with _Run(stdin, stdout) as run_:
		yield run_


@pytest.fixture
def stdin():
	return _ReadIoQueue()


@pytest.fixture
def stdout():
	return _WriteIoQueue()


class _Run:
	def __init__(self, stdin, stdout):
		self._process = None
		self._stdin = stdin
		self._stdout = stdout

	def _target(self, args):
		sys.stdin = self._stdin
		sys.stdout = self._stdout
		main(**parseArgs(args))

	def __enter__(self):
		def run_(*args):
			self._process = Process(target=self._target, args=(args,))
			self._process.start()

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


def getTestScope(project):
	scope = project.this['std', 'scope']
	scope['print'] = actl.objects.PyToA.call(lambda inp: print(f'mocked: {inp}'))
	return scope
