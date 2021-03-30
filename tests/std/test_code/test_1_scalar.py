from actl import opcodes
from actl.objects import Number, AToPy, Vector, Bool, String


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
	assert vector.getAttribute('__class__') is Vector
	assert Bool.call(vector) is Bool.False_


def test_vectorWithNumber(execute):
	execute('[1]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function=Vector.call),
		opcodes.CALL_FUNCTION_STATIC(dst='__IV12', function=String.call, args=['append']),
		opcodes.CALL_OPERATOR(dst='__IV13', first='__IV11', operator='.', second='__IV12'),
		opcodes.CALL_FUNCTION_STATIC(dst='__IV14', function=Number.call, args=['1']),
		opcodes.CALL_FUNCTION(dst='__IV0', function='__IV13', args=['__IV14']),
		opcodes.VARIABLE(name='__IV11')
	]
	vector = execute.executed.scope['_']
	assert vector.getAttribute('__class__') is Vector
	assert Bool.call(vector) is Bool.True_
