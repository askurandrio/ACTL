from actl import opcodes
from actl.objects import Number, AToPy


def test_varWithEndLine(execute):
	one = Number.call.obj(1).obj
	execute.scope['var'] = one

	execute('var\n')

	assert execute.parsed.code == [opcodes.VARIABLE(name='var')]
	assert execute.executed.scope['_'] == one


def test_setVariable(execute):
	execute('a = 1')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1', function=Number.call.obj, args=['1']
		),
		opcodes.SET_VARIABLE(dst='a', src='_tmpVar1')
	]
	assert AToPy(execute.executed.scope['a']) == 1
