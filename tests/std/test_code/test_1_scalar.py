from actl import opcodes
from actl.objects import Number, AToPy, Vector, Bool


def test_var(execute):
	one = Number.call(1)
	execute.scope['var'] = one

	execute('var')

	assert execute.parsed.code == [
		opcodes.VARIABLE(name='var')
	]
	assert execute.executed.scope['_'] == one


def test_floatNumber(execute):
	execute('1.1')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function=Number.call, args=['1.1']
		),
		opcodes.VARIABLE(name='__IV11')
	]
	assert AToPy(execute.executed.scope['_']) == 1.1


def test_negativeNumber(execute):
	execute('-1')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function=Number.call, args=['-1']
		),
		opcodes.VARIABLE(name='__IV11')
	]
	assert AToPy(execute.executed.scope['_']) == -1


def test_emptyVector(execute):
	execute('[]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function=Vector.call
		),
		opcodes.VARIABLE(name='__IV11')
	]
	vector = execute.executed.scope['_']
	assert vector.getAttr('__class__') is Vector
	assert Bool.call(vector) is Bool.False_
