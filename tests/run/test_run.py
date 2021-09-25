# pylint: disable=redefined-outer-name

import json

from actl.objects import PyToA, executeSyncCoroutine


def test_CtrlD(run):
	run()

	run.stdin.put('')
	assert run.stdout.get() == '>>> '


def test_setVar(run):
	run()
	assert run.stdout.get() == '>>> '
	run.stdin.put('a = 1\n')
	assert run.stdout.get() == '>>> '
	run.stdin.put('print(a)\n')
	assert run.stdout.get() == '1'
	assert run.stdout.get() == '\n'
	assert run.stdout.get() == '>>> '
	run.stdin.put('')


def test_expliciSetProjectF(run):
	run('--projectF', 'std/repl')

	run.stdin.put('')
	assert run.stdout.get() == '>>> '


def test_setExtraSource(run):
	extraSource = [
		{
			'py-externalKey': {
				'from': 'tests.run.test_run',
				'import': 'getInitialScope',
				'name': 'initialScope'
			}
		}
	]

	run('--source', json.dumps(extraSource))

	assert run.stdout.get() == '>>> '
	run.stdin.put('print(1)\n')
	assert run.stdout.get() == 'mocked: 1'
	assert run.stdout.get() == '\n'
	assert run.stdout.get() == '>>> '
	run.stdin.put('')


def test_explicitProjectFAndMainF(run):
	run('--projectF', 'std/base', '--mainF', 'tests/actl/example.a')

	assert run.stdout.get() == '1'
	assert run.stdout.get() == '\n'


def test_projectFAndMainF(run):
	run('std/base', 'tests/actl/example.a')

	assert run.stdout.get() == '1'
	assert run.stdout.get() == '\n'


def test_projectFAndMainFAndSource(run):
	extraSource = [
		{
			'py-externalKey': {
				'from': 'tests.run.test_run',
				'import': 'getInitialScope',
				'name': 'initialScope'
			}
		}
	]
	run('std/base', 'tests/actl/example.a', json.dumps(extraSource))

	assert run.stdout.get() == 'mocked: 1'
	assert run.stdout.get() == '\n'


def test_explicitMainF(run):
	run('--mainF', 'tests/actl/example.a')

	assert run.stdout.get() == '1'
	assert run.stdout.get() == '\n'


def test_mainF(run):
	run('tests/actl/example.a')

	assert run.stdout.get() == '1'
	assert run.stdout.get() == '\n'


def getInitialScope(project):
	scope = project.this['std/base', 'initialScope']
	scope['print'] = executeSyncCoroutine(PyToA.call(lambda inp: print(f'mocked: {inp}')))
	return scope
