from actl import opcodes
from actl.objects import Number


ORDER_KEY = 7


async def test_pointOperator(execute):
	execute('print.__call__')

	assert execute.parsed.code == [
		opcodes.GET_ATTRIBUTE(
			dst='_tmpVar1', object='print', attribute='__call__'
		),
		opcodes.VARIABLE(name='_tmpVar1')
	]

	assert execute.executed.scope['_tmpVar1'] == await execute.scope['print'].getAttribute('__call__')


async def test_add(execute):
	execute('1 + 2')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1', function=Number.call, args=['1']),
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar2', function=Number.call, args=['2']),
		opcodes.CALL_OPERATOR(dst='_tmpVar3', first='_tmpVar1', operator='+', second='_tmpVar2'),
		opcodes.VARIABLE(name='_tmpVar3')
	]


	assert execute.executed.scope['_tmpVar3'] == await Number.call('3')


async def test_setAddResult(execute):
	execute('a = 1 + 2')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1', function=Number.call, args=['1']),
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar2', function=Number.call, args=['2']),
		opcodes.CALL_OPERATOR(dst='_tmpVar3', first='_tmpVar1', operator='+', second='_tmpVar2'),
		opcodes.SET_VARIABLE('a', '_tmpVar3')
	]

	assert execute.executed.scope['a'] == await Number.call('3')
