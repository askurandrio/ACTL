# pylint: disable=redefined-outer-name

import sys
from multiprocessing import Queue, Process

import json
import pytest

from actl.run import main, buildArgParser


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
	run('--projectf', 'repl')

	stdin.put(':Ctrl^D')
	assert stdout.get() == '>>> '


def test_setExtraSource(run, stdin, stdout):
	extraSource = [
		{
			'py-key': {
				'name': 'scope',
				'code': '''
				import actl

				scope = this['std', 'scope']
				scope['print'] = actl.objects.PyToA.call(lambda inp: print(f'mocked: {inp}'))
				
				return scope
				'''
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
		args = buildArgParser().parse_args(args)
		main(args)

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
