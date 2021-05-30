from actl import opcodes
from actl.objects import Bool, Number


ORDER_KEY = 2


def test_emptyVector(execute):
	execute('[]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1', function=execute.scope['Vector'].call
		),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	vector = execute.executed.scope['_tmpVar1']
	assert vector.getAttribute('__class__') is execute.scope['Vector']


def test_vectorWithNumber(execute):
	execute('[1]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', execute.scope['Vector'].call),
		opcodes.GET_ATTRIBUTE('_tmpVar2', '_tmpVar1', 'append'),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar4', Number.call, args=['1']),
		opcodes.CALL_FUNCTION('_tmpVar3', '_tmpVar2', args=['_tmpVar4']),
		opcodes.VARIABLE(name='_tmpVar1')
	]
	vector = execute.executed.scope['_tmpVar1']
	assert vector.getAttribute('__class__') is execute.scope['Vector']
