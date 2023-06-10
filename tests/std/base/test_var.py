from actl import opcodes
from actl.objects import String, AToPy


ORDER_KEY = 2


async def test_varWithEndLine(execute):
	one = await String.call('a')
	execute.scope['var'] = one

	execute('var\n')

	assert execute.parsed.code == [opcodes.VARIABLE(name='var')]
	assert execute.executed


def test_setVariable(execute):
	execute('a = "a"')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1', function='String', staticArgs=['a']
		),
		opcodes.SET_VARIABLE(dst='a', src='_tmpVar1'),
	]
	assert AToPy(execute.executed.scope['a']) == 'a'
