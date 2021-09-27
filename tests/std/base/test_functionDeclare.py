from unittest.mock import Mock

from actl.objects import AToPy, PyToA, Number, Signature
from actl.opcodes import opcodes
from std.base.objects import Function


ORDER_KEY = 6


async def test_simpleFunctionDeclare(execute):
	mock = Mock()
	execute.initialScope['mock'] = await PyToA.call(mock)

	execute('fun f(): mock()\nf()')

	assert execute.parsed.code == [
		await Function.call(
			'f',
			await Signature.call([]),
			(
				opcodes.CALL_FUNCTION('_tmpVar1_1', 'mock'),
				opcodes.VARIABLE('_tmpVar1_1'),
				opcodes.RETURN('None')
			),
			None
		),
		opcodes.CALL_FUNCTION(dst='_tmpVar1', function='f', args=[]),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	assert AToPy(execute.executed.scope['_tmpVar1']) is None
	mock.assert_called_once_with()


async def test_declareMultiLineFunction(execute):
	mock = Mock()
	execute.initialScope['mock'] = await PyToA.call(mock)

	execute('fun f():\n a = 1\n mock(a)\nf()')

	assert execute.parsed.code == [
		await Function.call(
			'f',
			await Signature.call([]),
			(
				opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1_1', function=Number.call, args=['1']),
				opcodes.SET_VARIABLE(dst='a', src='_tmpVar1_1'),
				opcodes.CALL_FUNCTION(dst='_tmpVar1_2', function='mock', args=['a']),
				opcodes.VARIABLE(name='_tmpVar1_2'),
				opcodes.RETURN('None')
			),
			None
		),
		opcodes.CALL_FUNCTION(dst='_tmpVar1', function='f', args=[]),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	assert AToPy(execute.executed.scope['_tmpVar1']) is None
	mock.assert_called_once_with(1)


async def test_declareFunctionWithArg(execute):
	mock = Mock()
	execute.initialScope['mock'] = await PyToA.call(mock)

	execute('fun f(arg): mock(arg)\nf(1)')

	assert execute.parsed.code == [
		await Function.call(
			'f',
			await Signature.call(['arg']),
			(
				opcodes.CALL_FUNCTION('_tmpVar1_1', 'mock', args=['arg']),
				opcodes.VARIABLE('_tmpVar1_1'),
				opcodes.RETURN('None')
			),
			None
		),
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1', function=Number.call, args=['1']),
		opcodes.CALL_FUNCTION(dst='_tmpVar2', function='f', args=['_tmpVar1']),
		opcodes.VARIABLE(name='_tmpVar2')
	]

	assert AToPy(execute.executed.scope['_tmpVar2']) is None
	mock.assert_called_once_with(1)


async def test_functionWithReturn(execute):
	execute(
		'fun f():\n'
		'    return 1\n'
		'f()'
	)

	assert execute.parsed.code == [
		await Function.call(
			'f',
			await Signature.call([]),
			(
				opcodes.CALL_FUNCTION_STATIC('_tmpVar1_1', Number.call, args=['1']),
				opcodes.RETURN('_tmpVar1_1')
			),
			None
		),
		opcodes.CALL_FUNCTION('_tmpVar1', 'f', args=[]),
		opcodes.VARIABLE('_tmpVar1')
	]

	assert execute.executed.scope['_tmpVar1'] == await Number.call('1')



async def test_returnFromWhile(execute):
	execute(
		'fun f():\n'
		'    while True:\n'
		'        return 1\n'
		'f()'
	)

	assert execute.executed.scope['_tmpVar1'] == await Number.call('1')
