from actl import opcodes
from actl.objects.String import String
from std.objects import class_


def test_simple_class(execute):
	execute('class T:\n    a = 1')

	# assert execute.parsed.code == [
	# 	class_.call('T'),
	# 	opcodes.VARIABLE(name='T')
	# ]

	# assert execute.executed.scope['_'] == class_.call('T')
