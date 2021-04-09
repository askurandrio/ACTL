from actl import opcodes
from actl.objects.String import String
from std.objects import class_


def test_class(execute):
	execute('class T')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='T', function=class_.call, args=['T']
		),
		opcodes.VARIABLE(name='T')
	]

	assert execute.executed.scope['_'] == class_.call('T')
