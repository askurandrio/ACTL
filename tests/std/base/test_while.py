from unittest.mock import Mock

from actl import opcodes
from actl.objects import PyToA, Number
from std.base.objects import While


ORDER_KEY = 4


def test_simple_while(execute):
	def cond_():
		called, cond_.called = cond_.called, True
		return not called

	condIt = iter((True, False))
	cond = Mock(side_effect=lambda: next(condIt))
	print_ = Mock()
	execute.scope['cond'] = PyToA.call(cond)
	execute.initialScope['print'] = PyToA.call(print_)

	execute('while cond(): print(1)')

	cycle = execute.parsed.code.one()
	assert cycle.getAttribute('__class__') is While
	assert cycle.getAttribute('conditionFrame') == (
		opcodes.CALL_FUNCTION(dst='_tmpVar1', function='cond'),
		opcodes.VARIABLE(name='_tmpVar1')
	)
	assert cycle.getAttribute('code') == (
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1_1', function=Number.call, args=['1']),
		opcodes.CALL_FUNCTION(
			dst='_tmpVar1_2', function='print', args=['_tmpVar1_1']
		),
		opcodes.VARIABLE(name='_tmpVar1_2')
	)

	assert execute.executed
	assert cond.call_count == 2
	print_.assert_called_once_with(1)


def test_whileWithFullCodeBlock(execute):
	def cond_():
		called, cond_.called = cond_.called, True
		return not called

	cond_.called = False
	cond = Mock(side_effect=cond_)
	print_ = Mock()
	execute.scope['cond'] = PyToA.call(cond)
	execute.initialScope['print'] = PyToA.call(print_)

	execute('while cond():\n print(1)')

	cycle = execute.parsed.code.one()
	assert cycle.getAttribute('__class__') is While
	assert cycle.getAttribute('conditionFrame') == (
		opcodes.CALL_FUNCTION(dst='_tmpVar1', function='cond'),
		opcodes.VARIABLE(name='_tmpVar1')
	)
	assert cycle.getAttribute('code') == (
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1_1', function=Number.call, args=['1']),
		opcodes.CALL_FUNCTION(
			dst='_tmpVar1_2', function='print', args=['_tmpVar1_1']
		),
		opcodes.VARIABLE(name='_tmpVar1_2')
	)

	assert execute.executed
	assert cond.call_count == 2
	print_.assert_called_once_with(1)
