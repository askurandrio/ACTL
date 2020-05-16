from actl import opcodes
from actl.objects import String


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
