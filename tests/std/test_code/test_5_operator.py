from actl import opcodes
from actl.objects import String, Number


def test_pointOperator(execute):
	execute('print.__call__')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function=String.call, typeb='(', args=['__call__']
		),
		opcodes.CALL_OPERATOR(dst='__IV12', first='print', operator='.', second='__IV11'),
		opcodes.VARIABLE(name='__IV12')
	]

	assert execute.executed.scope['_'] is execute.scope['print'].getAttr('__call__')


def test_add(execute):
	execute('1 + 2')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function=Number.call, args=['1']),
		opcodes.CALL_FUNCTION_STATIC(dst='__IV13', function=Number.call, args=['2']),
		opcodes.CALL_OPERATOR(dst='__IV14', first='__IV11', operator='+', second='__IV13'),
		opcodes.VARIABLE(name='__IV14')
	]
