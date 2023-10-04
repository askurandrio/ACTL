from actl import opcodes
from actl.objects import String, AToPy


ORDER_KEY = 2


async def test_varWithEndLine(execute):
	one = await String.call('a')
	execute.scope['var'] = one

	execute('var\n')

	assert execute.parsed.code == [opcodes.VARIABLE(name='var')]
	assert execute.executed


async def test_setVariable(execute):
	execute('a = "a"')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='#1', function='String', staticArgs=['a']),
		opcodes.SET_VARIABLE(dst='a', src='#1'),
	]
	assert await AToPy(execute.executed.scope['a']) == 'a'
