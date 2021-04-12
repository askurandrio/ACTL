from actl import opcodes
from actl.objects import Number, AToPy, Vector, Bool, String


def test_var(execute):
	one = Number.call.obj(1).obj
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
	assert vector.getAttribute.obj('__class__').obj is Vector
	assert Bool.call.obj(vector).obj is Bool.False_


def test_vectorWithNumber(execute):
	execute('[1]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1', function=Vector.call.obj),
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar2', function=String.call.obj, args=['append']),
		opcodes.CALL_OPERATOR(dst='_tmpVar3', first='_tmpVar1', operator='.', second='_tmpVar2'),
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar4', function=Number.call.obj, args=['1']),
		opcodes.CALL_FUNCTION(dst='__IV0', function='_tmpVar3', args=['_tmpVar4']),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	vector = execute.executed.scope['_']
	assert vector.getAttribute.obj('__class__').obj is Vector
	assert Bool.call.obj(vector).obj is Bool.True_
