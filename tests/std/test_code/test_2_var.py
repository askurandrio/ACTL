from actl import opcodes
from actl.objects import Number, AToPy


def test_varWithEndLine(execute):
	one = Number.call(1)
	execute.scope['var'] = one

	execute('var\n')

	assert execute.parsed.code == [opcodes.VARIABLE(name='var')]
	assert execute.executed.scope['_'] == one


def test_setVariable(execute):
	execute('a = 1')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function=Number.call, typeb='(', args=['1'], kwargs={}
		),
		opcodes.SET_VARIABLE(dst='a', src='__IV11')
	]
	assert AToPy(execute.executed.scope['a']) == 1
