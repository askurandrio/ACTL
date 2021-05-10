from actl import opcodes
from actl.objects import Number, AToPy, Vector, Bool, String


ORDER_KEY = 1


def test_var(execute):
	one = Number.call(1).obj
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
			dst='_tmpVar1', function=Number.call.obj, args=['1.1']
		),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	assert AToPy(execute.executed.scope['_']) == 1.1


def test_negativeNumber(execute):
	execute('-1')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1', function=Number.call.obj, args=['-1']
		),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	assert AToPy(execute.executed.scope['_']) == -1


def test_emptyVector(execute):
	execute('[]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1', function=Vector.call.obj
		),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	vector = execute.executed.scope['_']
	assert vector.getAttribute('__class__').obj is Vector
	assert Bool.call(vector).obj is Bool.False_


def test_vectorWithNumber(execute):
	execute('[1]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', Vector.call.obj),
		opcodes.GET_ATTRIBUTE('_tmpVar2', '_tmpVar1', 'append'),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar4', Number.call.obj, args=['1']),
		opcodes.CALL_FUNCTION('_tmpVar3', '_tmpVar2', args=['_tmpVar4']),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	vector = execute.executed.scope['_']
	assert vector.getAttribute('__class__').obj is Vector
	assert Bool.call(vector).obj is Bool.True_
