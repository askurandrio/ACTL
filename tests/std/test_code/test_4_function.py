from unittest.mock import Mock

from actl.objects import AToPy, PyToA
from actl.opcodes import opcodes


def test_call(execute):
	print_ = Mock()
	execute.scope['print'] = PyToA.call(print_)

	execute('print()')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(dst='__IV11', function='print', typeb='(', args=[], kwargs={}),
		opcodes.VARIABLE(name='__IV11')
	]
	assert AToPy(execute.executed.scope['_']) == print_.return_value
	print_.assert_called_once()


def test_callWithString(execute):
	print_ = Mock()
	execute.scope['print'] = PyToA.call(print_)

	execute('print("s")')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function='String', args=['s']),
		opcodes.CALL_FUNCTION(
			dst='__IV12', function='print', typeb='(', args=['__IV11'], kwargs={}
		),
		opcodes.VARIABLE(name='__IV12')
	]
	assert AToPy(execute.executed.scope['_']) == print_.return_value
	print_.assert_called_once_with('s')


def test_function(execute):
	mock = Mock()
	execute.scope['print'] = PyToA.call(mock)

	execute('def f(): print()\nf()')

	setVar, _, _1 = execute.parsed.code
	assert setVar.dst == 'f'
	assert setVar.val.getAttr('signature') == ()
	assert setVar.val.getAttr('body') == (
		opcodes.CALL_FUNCTION(dst='__IV11', function='print', typeb='(', args=[], kwargs={}),
		opcodes.VARIABLE(name='__IV11'),
		opcodes.RETURN(var='None')
	)
	assert AToPy(execute.executed.scope['_']) is None
	mock.assert_called_once_with()
