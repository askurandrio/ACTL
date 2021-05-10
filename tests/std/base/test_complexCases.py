from actl import opcodes
from actl.objects import String


ORDER_KEY = 11


def test_setString(execute):
	execute("res = 's'")

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', String.call.obj, args=['s']),
		opcodes.SET_VARIABLE('res', '_tmpVar1')
	]
	assert execute.executed.scope['res'] == String.call('s').obj
