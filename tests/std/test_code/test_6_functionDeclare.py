from unittest.mock import Mock

from actl.objects import AToPy, PyToA, Number, Signature
from actl.opcodes import opcodes
from std.objects import Function


def test_simpleFunctionDeclare(execute):
	mock = Mock()
	execute.scope['print'] = PyToA.call(mock)

	execute('fun f(): print()\nf()')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='f',
			function=Function.call,
			args=(
				'f',
				Signature.call([]),
				[
					opcodes.CALL_FUNCTION(dst='__IV11', function='print'),
					opcodes.VARIABLE(name='__IV11')
				]
			)
		),
		opcodes.CALL_FUNCTION(dst='__IV12', function='f', args=[]),
		opcodes.VARIABLE(name='__IV12')
	]
	assert AToPy(execute.executed.scope['_']) is None
	mock.assert_called_once_with()


def test_declareMultiLineFunction(execute):
	mock = Mock()
	execute.scope['print'] = PyToA.call(mock)

	execute('fun f():\n a = 1\n print(a)\nf()')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='f',
			function=Function.call,
			args=(
				'f',
				Signature.call([]),
				[
					opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function=Number.call, args=['1']),
					opcodes.SET_VARIABLE(dst='a', src='__IV11'),
					opcodes.CALL_FUNCTION(dst='__IV12', function='print', args=['a']),
					opcodes.VARIABLE(name='__IV12')
				]
			)
		),
		opcodes.CALL_FUNCTION(dst='__IV13', function='f', args=[]),
		opcodes.VARIABLE(name='__IV13')
	]
	assert AToPy(execute.executed.scope['_']) is None
	mock.assert_called_once_with(1)


def test_declareFunctionWithArg(execute):
	mock = Mock()
	execute.scope['print'] = PyToA.call(mock)

	execute('fun f(arg): print(arg)\nf(1)')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='f',
			function=Function.call,
			args=(
				'f',
				Signature.call(['arg']),
				[
					opcodes.CALL_FUNCTION(dst='__IV11', function='print', args=['arg']),
					opcodes.VARIABLE(name='__IV11')
				]
			)
		),
		opcodes.CALL_FUNCTION_STATIC(dst='__IV12', function=Number.call, args=['1']),
		opcodes.CALL_FUNCTION(dst='__IV13', function='f', args=['__IV12']),
		opcodes.VARIABLE(name='__IV13')
	]

	assert AToPy(execute.executed.scope['_']) is None
	mock.assert_called_once_with(1)
