from actl import opcodes
from actl.objects import String, Number


def test_pointOperator(execute):
	execute('print.__call__')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1', function=String.call.obj, args=['__call__']
		),
		opcodes.CALL_OPERATOR(dst='_tmpVar2', first='print', operator='.', second='_tmpVar1'),
		opcodes.VARIABLE(name='_tmpVar2')
	]

	assert execute.executed.scope['_'] == execute.scope['print'].getAttribute.obj('__call__').obj


def test_add(execute):
	execute('1 + 2')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1', function=Number.call.obj, args=['1']),
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar2', function=Number.call.obj, args=['2']),
		opcodes.CALL_OPERATOR(dst='_tmpVar3', first='_tmpVar1', operator='+', second='_tmpVar2'),
		opcodes.VARIABLE(name='_tmpVar3')
	]
