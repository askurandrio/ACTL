from actl import opcodes
from actl.objects import Number
from std.objects import class_


def test_simpleClassDeclare(execute):
	execute('class T:\n    a = 1')

	assert execute.parsed.code == [
		class_.call(
			'T',
			{
				'body': (
					opcodes.CALL_FUNCTION_STATIC('_tmpVar1_1', function=Number.call, args=['1']),
					opcodes.SET_VARIABLE('a', '_tmpVar1_1')
				)
			}
		)
	]

	assert execute.executed.scope['T'] == class_.call(
		'T',
		{
			'a': Number.call(1)
		}
	)
