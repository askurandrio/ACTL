from actl import opcodes


ORDER_KEY = 8


def test_parseAddPropertyAndScalar(execute):
	execute('print.property + "a"')

	assert execute.parsed.code == [
		opcodes.GET_ATTRIBUTE('#1', 'print', 'property'),
		opcodes.CALL_FUNCTION_STATIC('#2', 'String', staticArgs=['a']),
		opcodes.CALL_OPERATOR('#3', '#1', '+', '#2'),
		opcodes.VARIABLE('#3'),
	]


def test_parseSetProperty(execute):
	execute('print.property = "a"')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC('#1', 'String', staticArgs=['a']),
		opcodes.SET_ATTRIBUTE('print', 'property', '#1'),
	]
