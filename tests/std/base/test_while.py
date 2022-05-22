from unittest.mock import Mock

from actl import opcodes
from actl.objects import PyToA, Number
from std.base.objects import While


ORDER_KEY = 4


async def test_simple_while(execute):
	def cond_():
		called, cond_.called = cond_.called, True
		return not called

	condIt = iter((True, False))
	conditionMock = Mock(side_effect=lambda: next(condIt))
	codeMock = Mock()
	execute.scope['conditionMock'] = await PyToA.call(conditionMock)
	execute.initialScope['codeMock'] = await PyToA.call(codeMock)

	execute('while conditionMock(): codeMock(1)')

	cycle = execute.parsed.code.one()
	assert await cycle.getAttribute('__class__') is While
	assert await cycle.getAttribute('conditionFrame') == (
		opcodes.CALL_FUNCTION(dst='_tmpVar1', function='conditionMock'),
		opcodes.VARIABLE(name='_tmpVar1'),
	)
	assert await cycle.getAttribute('code') == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1_1', function=Number.call, staticArgs=['1']
		),
		opcodes.CALL_FUNCTION(
			dst='_tmpVar1_2', function='codeMock', args=['_tmpVar1_1']
		),
		opcodes.VARIABLE(name='_tmpVar1_2'),
	)

	assert execute.executed
	assert conditionMock.call_count == 2
	codeMock.assert_called_once_with(1)


async def test_whileWithFullCodeBlock(execute):
	def cond_():
		called, cond_.called = cond_.called, True
		return not called

	cond_.called = False
	conditionMock = Mock(side_effect=cond_)
	codeMock = Mock()
	execute.scope['conditionMock'] = await PyToA.call(conditionMock)
	execute.initialScope['codeMock'] = await PyToA.call(codeMock)

	execute('while conditionMock():\n codeMock(1)')

	cycle = execute.parsed.code.one()
	assert await cycle.getAttribute('__class__') is While
	assert await cycle.getAttribute('conditionFrame') == (
		opcodes.CALL_FUNCTION(dst='_tmpVar1', function='conditionMock'),
		opcodes.VARIABLE(name='_tmpVar1'),
	)
	assert await cycle.getAttribute('code') == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1_1', function=Number.call, staticArgs=['1']
		),
		opcodes.CALL_FUNCTION(
			dst='_tmpVar1_2', function='codeMock', args=['_tmpVar1_1']
		),
		opcodes.VARIABLE(name='_tmpVar1_2'),
	)

	assert execute.executed
	assert conditionMock.call_count == 2
	codeMock.assert_called_once_with(1)
