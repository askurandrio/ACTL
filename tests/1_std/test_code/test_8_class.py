from unittest.mock import ANY

from actl import opcodes
from actl.objects import Number, Signature, String
from std.objects import class_, Function


def test_simpleClassDeclare(execute):
	execute(
		'class T:\n'
		'    a = 1'
	)

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


def test_classDeclareWithInitMethod(execute):
	execute(
		'class T:\n'
		'    fun __init__(self, a):\n'
		'        self.a = a\n'
	)

	assert execute.parsed.code == [
		class_.call(
			'T',
			{
				'body': (
					Function.call(
						'__init__',
						Signature.call(['self', 'a']),
						(
							opcodes.CALL_FUNCTION_STATIC(
								'_tmpVar2_1', function=String.call, args=['a']
							),
							opcodes.CALL_OPERATOR(
								'_tmpVar2_2', 'self', '.', '_tmpVar2_1'
							),
							opcodes.SET_VARIABLE('_tmpVar2_2', 'a'),
							opcodes.RETURN('None')
						),
						None
					),
				)
			}
		)
	]

	assert execute.executed.scope['T'] == class_.call(
		'T',
		{
			'__init__': Function.call(
            '__init__',
            Signature.call(['self', 'a']),
            (
               opcodes.CALL_FUNCTION_STATIC(
                  '_tmpVar2_1', function=String.call, args=['a']
               ),
               opcodes.CALL_OPERATOR(
                  '_tmpVar2_2', 'self', '.', '_tmpVar2_1'
               ),
               opcodes.SET_VARIABLE('_tmpVar2_2', 'a'),
               opcodes.RETURN('None')
            ),
            ANY
         )
		}
	)
