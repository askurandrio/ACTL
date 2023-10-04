# pylint: disable=redefined-outer-name

from unittest.mock import Mock

import pytest

from actl.objects import AToPy, PyToA
from actl.opcodes import opcodes


ORDER_KEY = 5


@pytest.mark.parametrize(
	["code", "args", "kwargs"],
	[
		['testF()', [], {}],
		['testF( )', [], {}],
		['testF(\n)', [], {}],
		['testF(arg)', ["arg"], {}],
		['testF( arg )', ["arg"], {}],
		['testF(\narg\n)', ["arg"], {}],
		['testF(first, second)', ["first", "second"], {}],
		['testF(first,second)', ["first", "second"], {}],
		['testF( first , second )', ["first", "second"], {}],
		['testF(\nfirst\n,\nsecond\n)', ["first", "second"], {}],
		['testF(argName=arg)', [], {'argName': 'arg'}],
		['testF(first, secondName=second)', ["first"], {'secondName': 'second'}],
	],
)
async def test_calls(execute, testF, code, args, kwargs):
	arg_values = [Mock() for _ in args]
	kwarg_values = {name: Mock() for name in kwargs.values()}

	for name, mock in (*zip(args, arg_values), *kwarg_values.items()):
		execute.scope[name] = await PyToA.call(mock)

	execute(code)

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(dst='#1', function='testF', args=args, kwargs=kwargs),
		opcodes.VARIABLE(name='#1'),
	]
	assert await AToPy(execute.executed.scope['#1']) == testF.return_value
	testF.assert_called_once_with(
		*arg_values, **{key: kwarg_values[value] for key, value in kwargs.items()}
	)


async def test_callWithString(execute, testF):
	execute('testF("s")')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='#1', function='String', staticArgs=['s']),
		opcodes.CALL_FUNCTION(dst='#2', function='testF', args=['#1']),
		opcodes.VARIABLE(name='#2'),
	]
	assert await AToPy(execute.executed.scope['#2']) == testF.return_value
	testF.assert_called_once_with('s')


@pytest.fixture
async def testF(execute):
	mock = Mock()
	execute.scope['testF'] = await PyToA.call(mock)

	return mock
