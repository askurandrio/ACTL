# pylint: disable=redefined-outer-name

import json

from actl.objects import PyToA
from actl.utils import executeSyncCoroutine


def test_invitation(run):
	run()

	run.readTemplate('>>> ')


def test_setVar(run):
	run()

	run.writeLine('a = 1')
	run.writeLine('print(a)')
	assert run.readLine() == '>>> >>> 1\n'
	run.readTemplate('>>> ')


def test_expliciSetProjectF(run):
	run('--projectF', 'std/repl')

	run.readTemplate('>>> ')


def test_setExtraSource(run):
	extraSource = [
		{
			'py-externalKey': {
				'from': 'tests.run.test_run',
				'import': 'getInitialScope',
				'name': 'initialScope',
			}
		}
	]

	run('--source', json.dumps(extraSource))

	run.writeLine('print(1)')
	assert run.readLine() == '>>> mocked: 1\n'
	run.readTemplate('>>> ')


def test_explicitProjectFAndMainF(run):
	run('--projectF', 'std/base', '--mainF', 'tests/actl/example.a')

	assert run.readLine() == '1\n'


def test_projectFAndMainF(run):
	run('std/base', 'tests/actl/example.a')

	assert run.readLine() == '1\n'


def test_projectFAndMainFAndSource(run):
	extraSource = [
		{
			'py-externalKey': {
				'from': 'tests.run.test_run',
				'import': 'getInitialScope',
				'name': 'initialScope',
			}
		}
	]
	run('std/base', 'tests/actl/example.a', json.dumps(extraSource))

	assert run.readLine() == 'mocked: 1\n'


def test_explicitMainF(run):
	run('--mainF', 'tests/actl/example.a')

	assert run.readLine() == '1\n'


def test_mainF(run):
	run('tests/actl/example.a')

	assert run.readLine() == '1\n'


def getInitialScope(project):
	scope = project['std/base', 'initialScope']
	scope['print'] = executeSyncCoroutine(
		PyToA.call(lambda inp: print(f'mocked: {inp}'))
	)
	return scope
