from unittest.mock import Mock

from actl import opcodes
from actl.objects import PyToA, AToPy, Number
from std.objects import While


def test_while(execute):
	def cond_():
		called, cond_.called = cond_.called, True
		return not called

	cond_.called = False
	cond = Mock(side_effect=cond_)
	print_ = Mock()
	execute.scope['cond'] = PyToA.call(cond)
	execute.scope['print'] = PyToA.call(print_)

	execute('while cond(): print(1)')

	cycle = execute.parsed.code.one()
	assert cycle.class_ is While
	assert cycle.getAttr('conditionFrame') == (
		opcodes.CALL_FUNCTION(dst='__IV11', function='cond', typeb='(', args=[], kwargs={}),
		opcodes.VARIABLE(name='__IV11')
	)
	assert cycle.getAttr('code') == (
		opcodes.CALL_FUNCTION_STATIC(dst='__IV12', function=Number.call, args=['1']),
		opcodes.CALL_FUNCTION(
			dst='__IV13', function='print', typeb='(', args=['__IV12'], kwargs={}
		),
		opcodes.VARIABLE(name='__IV13')
	)

	assert not AToPy(execute.executed.scope['_'])
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
	execute.scope['print'] = PyToA.call(print_)

	execute('while cond():\n print(1)')

	cycle = execute.parsed.code.one()
	assert cycle.class_ is While
	assert cycle.getAttr('conditionFrame') == (
		opcodes.CALL_FUNCTION(dst='__IV11', function='cond', typeb='(', args=[], kwargs={}),
		opcodes.VARIABLE(name='__IV11')
	)
	assert cycle.getAttr('code') == (
		opcodes.CALL_FUNCTION_STATIC(dst='__IV12', function=Number.call, args=['1']),
		opcodes.CALL_FUNCTION(
			dst='__IV13', function='print', typeb='(', args=['__IV12'], kwargs={}
		),
		opcodes.VARIABLE(name='__IV13')
	)

	assert not AToPy(execute.executed.scope['_'])
	assert cond.call_count == 2
	print_.assert_called_once_with(1)
