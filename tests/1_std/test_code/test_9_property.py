from actl import opcodes
from actl.objects import Number


def test_parseAddPropertyAndScalar(execute):
	execute('print.property + 1')

	assert execute.parsed.code == [
		opcodes.GET_ATTRIBUTE('_tmpVar1', 'print', 'property'),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar2', Number.call.obj, args=['1']),
		opcodes.CALL_OPERATOR('_tmpVar3', '_tmpVar1', '+', '_tmpVar2'),
		opcodes.VARIABLE('_tmpVar3')
	]


def test_parseSetProperty(execute):
	execute('print.property = 1')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', Number.call.obj, args=['1']),
		opcodes.SET_ATTRIBUTE('print', 'property', '_tmpVar1')
	]
