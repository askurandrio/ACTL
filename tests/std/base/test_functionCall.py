from unittest.mock import Mock

import pytest

from actl.objects import AToPy, PyToA, String
from actl.opcodes import opcodes


ORDER_KEY = 5


def test_call(execute, testF):
	execute('testF()')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(dst='_tmpVar1', function='testF'),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	assert AToPy(execute.executed.scope['_']) == testF.return_value
	testF.assert_called_once_with()


def test_callWithArg(execute, testF):
	arg = Mock()
	execute.scope['arg'] = PyToA.call(arg)

	execute('testF(arg)')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(dst='_tmpVar1', function='testF', args=['arg']),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	assert AToPy(execute.executed.scope['_']) == testF.return_value
	testF.assert_called_once_with(arg)


def test_callWithString(execute, testF):
	execute('testF("s")')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1', function=String.call, args=['s']),
		opcodes.CALL_FUNCTION(
			dst='_tmpVar2', function='testF', args=['_tmpVar1']
		),
		opcodes.VARIABLE(name='_tmpVar2')
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
			dst='_tmpVar1', function='testF', args=['first', 'second']
		),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	assert AToPy(execute.executed.scope['_']) == testF.return_value
	testF.assert_called_once_with(first, second)


def test_callWithNamedArg(execute, testF):
	arg = Mock()
	execute.scope['arg'] = PyToA.call(arg)

	execute('testF(argName=arg)')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(
			dst='_tmpVar1', function='testF', kwargs={'argName': 'arg'}
		),
		opcodes.VARIABLE(name='_tmpVar1')
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
			dst='_tmpVar1', function='testF', args=['first'], kwargs={'secondName': 'second'}
		),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	assert AToPy(execute.executed.scope['_']) == testF.return_value
	testF.assert_called_once_with(first, secondName=second)


@pytest.fixture
def testF(execute):
	mock = Mock()
	execute.scope['testF'] = PyToA.call(mock)

	return mock
