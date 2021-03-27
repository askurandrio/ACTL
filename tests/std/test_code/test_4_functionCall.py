from unittest.mock import Mock

import pytest

from actl.objects import AToPy, PyToA, String
from actl.opcodes import opcodes


def test_call(execute, testF):
	execute('testF()')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(dst='__IV11', function='testF', typeb='(', args=[], kwargs={}),
		opcodes.VARIABLE(name='__IV11')
	]
	assert AToPy(execute.executed.scope['_']) == testF.return_value
	testF.assert_called_once_with()


def test_callWithArg(execute, testF):
	arg = Mock()
	execute.scope['arg'] = PyToA.call(arg)

	execute('testF(arg)')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(dst='__IV11', function='testF', typeb='(', args=['arg'], kwargs={}),
		opcodes.VARIABLE(name='__IV11')
	]
	assert AToPy(execute.executed.scope['_']) == testF.return_value
	testF.assert_called_once_with(arg)


def test_callWithString(execute, testF):
	execute('testF("s")')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function=String.call, args=['s']),
		opcodes.CALL_FUNCTION(
			dst='__IV12', function='testF', typeb='(', args=['__IV11'], kwargs={}
		),
		opcodes.VARIABLE(name='__IV12')
	]
	assert AToPy(execute.executed.scope['_']) == testF.return_value
	testF.assert_called_once_with('s')


def test_callWithTwoArg(execute, testF):
	first = Mock()
	second = Mock()
	execute.scope['first'] = PyToA.call(first)
	execute.scope['second'] = PyToA.call(second)

	execute('testF(first, second)')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(
			dst='__IV11', function='testF', typeb='(', args=['first', 'second'], kwargs={}
		),
		opcodes.VARIABLE(name='__IV11')
	]
	assert AToPy(execute.executed.scope['_']) == testF.return_value
	testF.assert_called_once_with(first, second)


def test_callWithNamedArg(execute, testF):
	arg = Mock()
	execute.scope['arg'] = PyToA.call(arg)

	execute('testF(argName=arg)')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(
			dst='__IV11', function='testF', typeb='(', args=[], kwargs={'argName': 'arg'}
		),
		opcodes.VARIABLE(name='__IV11')
	]
	assert AToPy(execute.executed.scope['_']) == testF.return_value
	testF.assert_called_once_with(argName=arg)


def test_callWithArgAndNamedArg(execute, testF):
	first = Mock()
	second = Mock()
	execute.scope['first'] = PyToA.call(first)
	execute.scope['second'] = PyToA.call(second)

	execute('testF(first, secondName=second)')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(
			dst='__IV11', function='testF', typeb='(', args=['first'], kwargs={'secondName': 'second'}
		),
		opcodes.VARIABLE(name='__IV11')
	]
	assert AToPy(execute.executed.scope['_']) == testF.return_value
	testF.assert_called_once_with(first, secondName=second)


@pytest.fixture
def testF(execute):
	mock = Mock()
	execute.scope['testF'] = PyToA.call(mock)

	return mock
