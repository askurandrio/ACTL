from actl import opcodes
from actl.objects import String


ORDER_KEY = 1


async def test_var(execute):
	one = await String.call('a')
	execute.scope['var'] = one

	execute('var')

	assert execute.parsed.code == [opcodes.VARIABLE(name='var')]
	assert execute.executed
