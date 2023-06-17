# pylint: disable=redefined-outer-name

from unittest.mock import Mock

import pytest

from actl.objects import AToPy, PyToA
from actl.opcodes import opcodes


ORDER_KEY = 5


@pytest.mark.parametrize(
	["code", "args"],
	[
		['testF()', []],
		['testF( )', []],
		['testF(\n)', []],
		['testF(arg)', ["arg"]],
		['testF( arg )', ["arg"]],
		['testF(\narg\n)', ["arg"]],
		['testF(first, second)', ["first", "second"]],
		['testF(first,second)', ["first", "second"]],
		['testF( first , second )', ["first", "second"]],
		['testF(\nfirst\n,\nsecond\n)', ["first", "second"]],
	],
)
async def test_calls(execute, testF, code, args):
	mocks = [Mock() for _ in args]
	for name, mock in zip(args, mocks):
		execute.scope[name] = await PyToA.call(mock)

	execute(code)

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(dst='_tmpVar1', function='testF', args=args),
		opcodes.VARIABLE(name='_tmpVar1'),
	]
	assert AToPy(execute.executed.scope['_tmpVar1']) == testF.return_value
	testF.assert_called_once_with(*mocks)


async def test_callWithString(execute, testF):
	execute('testF("s")')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1', function='String', staticArgs=['s']
		),
		opcodes.CALL_FUNCTION(dst='_tmpVar2', function='testF', args=['_tmpVar1']),
		opcodes.VARIABLE(name='_tmpVar2'),
	]
	assert AToPy(execute.executed.scope['_tmpVar2']) == testF.return_value
	testF.assert_called_once_with('s')


async def test_callWithNamedArg(execute, testF):
	arg = Mock()
	execute.scope['arg'] = await PyToA.call(arg)

	execute('testF(argName=arg)')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(
			dst='_tmpVar1', function='testF', kwargs={'argName': 'arg'}
		),
		opcodes.VARIABLE(name='_tmpVar1'),
	]
	assert AToPy(execute.executed.scope['_tmpVar1']) == testF.return_value
	testF.assert_called_once_with(argName=arg)


async def test_callWithArgAndNamedArg(execute, testF):
	first = Mock()
	second = Mock()
	execute.scope['first'] = await PyToA.call(first)
	execute.scope['second'] = await PyToA.call(second)

	execute('testF(first, secondName=second)')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(
			dst='_tmpVar1',
			function='testF',
			args=['first'],
			kwargs={'secondName': 'second'},
		),
		opcodes.VARIABLE(name='_tmpVar1'),
	]
	assert AToPy(execute.executed.scope['_tmpVar1']) == testF.return_value
	testF.assert_called_once_with(first, secondName=second)


@pytest.fixture
async def testF(execute):
	mock = Mock()
	execute.scope['testF'] = await PyToA.call(mock)

	return mock
