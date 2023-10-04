from unittest.mock import Mock

from actl.objects import AToPy, PyToA, Signature
from actl.opcodes import opcodes
from std.base.objects import Function


ORDER_KEY = 6


async def test_simpleFunctionDeclare(execute):
	mock = Mock()
	execute.initialScope['mock'] = await PyToA.call(mock)

	execute('fun f(): mock()\nf()')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			'f',
			Function.call,
			staticArgs=(
				'f',
				await Signature.call(()),
				(
					opcodes.CALL_FUNCTION('#1_1', 'mock'),
					opcodes.VARIABLE('#1_1'),
					opcodes.RETURN('None'),
				),
			),
			kwargs={'scope': '__scope__'},
		),
		opcodes.CALL_FUNCTION(dst='#1', function='f', args=[]),
		opcodes.VARIABLE(name='#1'),
	]
	assert AToPy(execute.executed.scope['#1']) is None
	mock.assert_called_once_with()


async def test_declareMultiLineFunction(execute):
	mock = Mock()
	execute.initialScope['mock'] = await PyToA.call(mock)

	execute('fun f():\n a = "a"\n mock(a)\nf()')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			'f',
			Function.call,
			staticArgs=(
				'f',
				await Signature.call(()),
				(
					opcodes.CALL_FUNCTION_STATIC(
						dst='#1_1', function='String', staticArgs=['a']
					),
					opcodes.SET_VARIABLE(dst='a', src='#1_1'),
					opcodes.CALL_FUNCTION(dst='#1_2', function='mock', args=['a']),
					opcodes.VARIABLE(name='#1_2'),
					opcodes.RETURN('None'),
				),
			),
			kwargs={'scope': '__scope__'},
		),
		opcodes.CALL_FUNCTION(dst='#1', function='f', args=[]),
		opcodes.VARIABLE(name='#1'),
	]
	assert AToPy(execute.executed.scope['#1']) is None
	mock.assert_called_once_with('a')


async def test_declareFunctionWithArg(execute):
	mock = Mock()
	execute.initialScope['mock'] = await PyToA.call(mock)

	execute('fun f(arg): mock(arg)\nf("a")')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			'f',
			Function.call,
			staticArgs=(
				'f',
				await Signature.call(('arg',)),
				(
					opcodes.CALL_FUNCTION('#1_1', 'mock', args=['arg']),
					opcodes.VARIABLE('#1_1'),
					opcodes.RETURN('None'),
				),
			),
			kwargs={'scope': '__scope__'},
		),
		opcodes.CALL_FUNCTION_STATIC(dst='#1', function='String', staticArgs=['a']),
		opcodes.CALL_FUNCTION(dst='#2', function='f', args=['#1']),
		opcodes.VARIABLE(name='#2'),
	]

	assert AToPy(execute.executed.scope['#2']) is None
	mock.assert_called_once_with('a')


async def test_functionWithReturn(execute):
	execute('fun f():\n	return "a"\nf()')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			'f',
			Function.call,
			staticArgs=(
				'f',
				await Signature.call(()),
				(
					opcodes.CALL_FUNCTION_STATIC('#1_1', 'String', staticArgs=['a']),
					opcodes.RETURN('#1_1'),
				),
			),
			kwargs={'scope': '__scope__'},
		),
		opcodes.CALL_FUNCTION('#1', 'f', args=[]),
		opcodes.VARIABLE('#1'),
	]

	assert AToPy(execute.executed.scope['#1']) == 'a'


async def test_returnFromWhile(execute):
	execute('fun f():\n	while True:\n		return "a"\nf()')

	assert AToPy(execute.executed.scope['#1']) == 'a'
