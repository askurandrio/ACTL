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


@pytest.fixture
def testF(execute):
	mock = Mock()
	execute.scope['testF'] = PyToA.call(mock)

	return mock
