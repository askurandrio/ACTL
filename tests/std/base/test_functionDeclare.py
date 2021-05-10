from unittest.mock import Mock

from actl.objects import AToPy, PyToA, Number, Signature
from actl.opcodes import opcodes
from std.base.objects import Function


ORDER_KEY = 6


def test_simpleFunctionDeclare(execute):
	mock = Mock()
	execute.initialScope['print'] = PyToA.call(mock).obj

	execute('fun f(): print()\nf()')

	assert execute.parsed.code == [
		Function.call(
			'f',
			Signature.call([]).obj,
			(
				opcodes.CALL_FUNCTION('_tmpVar1_1', 'print'),
				opcodes.VARIABLE('_tmpVar1_1'),
				opcodes.RETURN('None')
			),
			None
		).obj,
		opcodes.CALL_FUNCTION(dst='_tmpVar1', function='f', args=[]),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	assert AToPy(execute.executed.scope['_']) is None
	mock.assert_called_once_with()


def test_declareMultiLineFunction(execute):
	mock = Mock()
	execute.initialScope['print'] = PyToA.call(mock).obj

	execute('fun f():\n a = 1\n print(a)\nf()')

	assert execute.parsed.code == [
		Function.call(
			'f',
			Signature.call([]).obj,
			(
				opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1_1', function=Number.call.obj, args=['1']),
				opcodes.SET_VARIABLE(dst='a', src='_tmpVar1_1'),
				opcodes.CALL_FUNCTION(dst='_tmpVar1_2', function='print', args=['a']),
				opcodes.VARIABLE(name='_tmpVar1_2'),
				opcodes.RETURN('None')
			),
			None
		).obj,
		opcodes.CALL_FUNCTION(dst='_tmpVar1', function='f', args=[]),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	assert AToPy(execute.executed.scope['_']) is None
	mock.assert_called_once_with(1)


def test_declareFunctionWithArg(execute):
	mock = Mock()
	execute.initialScope['print'] = PyToA.call(mock).obj

	execute('fun f(arg): print(arg)\nf(1)')

	assert execute.parsed.code == [
		Function.call(
			'f',
			Signature.call(['arg']).obj,
			(
				opcodes.CALL_FUNCTION('_tmpVar1_1', 'print', args=['arg']),
				opcodes.VARIABLE('_tmpVar1_1'),
				opcodes.RETURN('None')
			),
			None
		).obj,
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1', function=Number.call.obj, args=['1']),
		opcodes.CALL_FUNCTION(dst='_tmpVar2', function='f', args=['_tmpVar1']),
		opcodes.VARIABLE(name='_tmpVar2')
	]

	assert AToPy(execute.executed.scope['_']) is None
	mock.assert_called_once_with(1)


def test_functionWithReturn(execute):
	mock = Mock()
	execute.initialScope['print'] = PyToA.call(mock).obj

	execute(
		'fun f():\n'
		'    return 1\n'
		'f()'
	)

	assert execute.parsed.code == [
		Function.call(
			'f',
			Signature.call([]).obj,
			(
				opcodes.CALL_FUNCTION_STATIC('_tmpVar1_1', Number.call.obj, args=['1']),
				opcodes.RETURN('_tmpVar1_1')
			),
			None
		).obj,
		opcodes.CALL_FUNCTION('_tmpVar1', 'f', args=[]),
		opcodes.VARIABLE('_tmpVar1')
	]

	assert execute.executed.scope['_tmpVar1'] == Number.call('1').obj
