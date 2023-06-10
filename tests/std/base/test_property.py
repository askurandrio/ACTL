from actl import opcodes


ORDER_KEY = 8


def test_parseAddPropertyAndScalar(execute):
	execute('print.property + "a"')

	assert execute.parsed.code == [
		opcodes.GET_ATTRIBUTE('_tmpVar1', 'print', 'property'),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar2', 'String', staticArgs=['a']),
		opcodes.CALL_OPERATOR('_tmpVar3', '_tmpVar1', '+', '_tmpVar2'),
		opcodes.VARIABLE('_tmpVar3'),
	]


def test_parseSetProperty(execute):
	execute('print.property = "a"')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', 'String', staticArgs=['a']),
		opcodes.SET_ATTRIBUTE('print', 'property', '_tmpVar1'),
	]
