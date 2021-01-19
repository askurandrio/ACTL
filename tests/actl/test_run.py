# pylint: disable=redefined-outer-name

import sys
from multiprocessing import Queue, Process

import json
import pytest

import actl
from actl.run import main, parseArgs


class _WriteIoQueue:
	def __init__(self):
		self._queue = Queue()

	def write(self, content):
		self._queue.put(content)

	def get(self):
		return self._queue.get(timeout=5)


class _ReadIoQueue:
	def __init__(self):
		self._queue = Queue()

	def put(self, line):
		self._queue.put(line)

	def readline(self):
		line = self._queue.get(timeout=5)
		if line == ':Ctrl^D':
			raise EOFError(line)
		return line


def test_simpleRepl(run, stdin, stdout):
	run()

	stdin.put(':Ctrl^D')
	assert stdout.get() == '>>> '


def test_expliciSetProjectF(run, stdin, stdout):
	run('--projectF', 'repl')

	stdin.put(':Ctrl^D')
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
	stdin.put('print(1)')
	assert stdout.get() == ''
	assert stdout.get() == '\n'
	assert stdout.get() == '>>> '
	stdin.put(':Ctrl^D')
	assert stdout.get() == 'mocked: 1'


@pytest.fixture
def run(stdin, stdout):
	def _target(args, stdin, stdout):
		sys.stdin = stdin
		sys.stdout = stdout
		main(**parseArgs(args))

	process = None

	def run_(*args):
		nonlocal process
		process = Process(target=_target, args=(args, stdin, stdout))
		process.start()

	yield run_

	process.join(timeout=5)
	try:
		assert not process.is_alive()
	except AssertionError:
		process.terminate()
		raise


@pytest.fixture
def stdin():
	return _ReadIoQueue()


@pytest.fixture
def stdout():
	return _WriteIoQueue()


def getTestScope(project):
	scope = project.this['std', 'scope']
	scope['print'] = actl.objects.PyToA.call(lambda inp: print(f'mocked: {inp}'))
	return scope
