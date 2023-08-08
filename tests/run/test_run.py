# pylint: disable=redefined-outer-name

import json

from actl.objects import PyToA
from actl.utils import executeSyncCoroutine


def test_invitation(run):
	run()

	run.readTemplate('>>> ')


def test_setVar(run):
	run()

	run.readTemplate('>>> ')
	run.writeLine('a = "a"')
	run.readTemplate('>>> ')
	run.writeLine('print(a)')
	assert run.readLine() == "a\n"
	assert run.readLine() == "None\n"
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

	run.readTemplate('>>> ')
	run.writeLine('print("a")')
	assert run.readLine() == 'mocked: a\n'
	assert run.readLine() == "mocked: None\n"
	run.readTemplate('>>> ')


def test_explicitProjectFAndMainFAndSource(run):
	extraSource = [
		{
			'py-externalKey': {
				'from': 'tests.run.test_run',
				'import': 'getInitialScope',
				'name': 'initialScope',
			}
		}
	]
	run(
		'--projectF',
		'std',
		'--mainF',
		'tests/actl/example.a',
		'--source',
		json.dumps(extraSource),
	)

	assert run.readLine() == 'mocked: a\n'


def test_mainF(run):
	run('tests/actl/example.a')

	assert run.readLine() == 'a\n'


def test_changeInvitation(run):
	run()

	run.writeLine('fun f():')
	run.writeLine('\ta = 1')
	run.writeLine('f()')

	assert (
		run.readLine().strip()
		== """>>> ... ... fun f(): (CALL_FUNCTION_STATIC('_tmpVar1_1', 'Number', typeb='(', staticArgs=[PyToA<1>], staticKwargs={}, args=[], kwargs={}), SET_VARIABLE('a', '_tmpVar1_1'), RETURN('None'))"""
	)
	assert run.readLine() == 'None\n'
	run.readTemplate('>>> ')


def test_processEmptyLine(run):
	run()

	run.writeLine('')

	run.readTemplate('>>> ')
	run.readTemplate('>>> ')


def test_envVarCODE(run):
	run(env={'CODE': 'print(1)'})

	assert run.readLine() == 'Number<_head=PyToA<1>>\n'
	assert run.readLine() == 'None\n'


def getInitialScope(project):
	scope = project['std/base', 'initialScope']
	scope['print'] = executeSyncCoroutine(
		PyToA.call(lambda inp: print(f'mocked: {inp}'))
	)
	return scope


def test_main(run):
	run('tests/run/test_main.a')

	assert run.readLine() == 'a\n'


def test_mainWithArgv(run, tmp_path):
	fileName = tmp_path / 'example.a'
	fileName.write_text('fun main(arg):\n\tprint("arg", arg)')

	run(fileName, '1')

	assert run.readLine() == 'arg 1\n'
