from unittest.mock import ANY, Mock

from actl import opcodes
from actl.objects import Number, Signature, String, PyToA
from std.objects import class_, Function


def test_simpleClassDeclare(execute):
	execute(
		'class T:\n'
		'    a = 1'
	)

	assert execute.parsed.code == [
		class_.call.obj(
			'T',
			{
				'body': (
					opcodes.CALL_FUNCTION_STATIC('_tmpVar1_1', function=Number.call.obj, args=['1']),
					opcodes.SET_VARIABLE('a', '_tmpVar1_1')
				)
			}
		).obj
	]

	assert execute.executed.scope['T'] == class_.call.obj(
		'T',
		{
			'a': Number.call.obj(1).obj
		}
	).obj


def test_classDeclareWithInitMethod(execute):
	execute(
		'class T:\n'
		'    fun __init__(self, a):\n'
		'        self.a = a\n'
	)

	assert execute.parsed.code == [
		class_.call.obj(
			'T',
			{
				'body': (
					Function.call.obj(
						'__init__',
						Signature.call.obj(['self', 'a']).obj,
						(
							opcodes.SET_ATTRIBUTE('self', 'a', 'a'),
							opcodes.RETURN('None')
						),
						None
					).obj,
				)
			}
		).obj
	]

	assert execute.executed.scope['T'] == class_.call.obj(
		'T',
		{
			'__self__': {
				'__init__': Function.call.obj(
					'__init__',
					Signature.call.obj(['self', 'a']).obj,
					(
						opcodes.SET_ATTRIBUTE('self', 'a', 'a'),
						opcodes.RETURN('None')
					),
					ANY
				).obj
			}
		}
	).obj


def test_classUseWithInitMethod(execute):
	mock = Mock()
	execute.scope['print'] = PyToA.call.obj(mock).obj

	execute(
		'class T:\n'
		'    fun __init__(self):\n'
		'        self.a = 1\n'
		't = T()\n'
	)

	assert execute.parsed.code == [
		class_.call.obj(
			'T',
			{
				'body': (
					Function.call.obj(
						'__init__',
						Signature.call.obj(['self']).obj,
						(
							opcodes.CALL_FUNCTION_STATIC(
								'_tmpVar2_1', function=Number.call.obj, args=['1']
							),
							opcodes.SET_ATTRIBUTE('self', 'a', '_tmpVar2_1'),
							opcodes.RETURN('None')
						),
						None
					).obj,
				)
			}
		).obj,
		opcodes.CALL_FUNCTION('_tmpVar1', 'T'),
		opcodes.SET_VARIABLE('t', '_tmpVar1')
	]

	assert execute.executed.scope['T'] == class_.call.obj(
		'T',
		{
			'__self__': {
				'__init__': Function.call.obj(
					'__init__',
					Signature.call.obj(['self']).obj,
					(
						opcodes.CALL_FUNCTION_STATIC(
							'_tmpVar2_1', function=Number.call.obj, args=['1']
						),
						opcodes.SET_ATTRIBUTE('self', 'a', '_tmpVar2_1'),
						opcodes.RETURN('None')
					),
					ANY
				).obj
			}
		}
	).obj
	assert str(String.call.obj(execute.executed.scope['t']).obj) == "T<{'a': Number<1>}>"
