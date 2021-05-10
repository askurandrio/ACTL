from unittest.mock import ANY

from actl import opcodes
from actl.objects import Number, Signature, String, PyToA
from std.base.objects import class_, Function


ORDER_KEY = 9


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


def test_classWithInitMethod(execute):
	execute(
		'class C:\n'
		'    fun __init__(self, a):\n'
		'        self.a = a\n'
		'c = C(1)'
	)

	assert execute.parsed.code == [
		class_.call.obj(
			'C',
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
		).obj,
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', Number.call.obj, args=['1']),
		opcodes.CALL_FUNCTION('_tmpVar2', 'C', args=['_tmpVar1']),
		opcodes.SET_VARIABLE('c', '_tmpVar2')
	]

	assert execute.executed.scope['C'] == class_.call.obj(
		'C',
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
	assert str(String.call.obj(execute.executed.scope['c']).obj) == "C<{'a': Number<1>}>"


def test_classWithMethod(execute):
	execute(
		'class C:\n'
		'    fun method(self, a):\n'
		'        self.a = a\n'
	   '        a = self.a + 2\n'
		'        return a\n'
		'c = C()\n'
		'tMethodResult = c.method(1)'
	)

	assert execute.parsed.code == [
		class_.call.obj(
			'C',
			{
				'body': (
					Function.call.obj(
						'method',
						Signature.call.obj(['self', 'a']).obj,
						(
							opcodes.SET_ATTRIBUTE('self', 'a', 'a'),
							opcodes.GET_ATTRIBUTE('_tmpVar2_1', 'self', 'a'),
							opcodes.CALL_FUNCTION_STATIC('_tmpVar2_2', Number.call.obj, args=['2']),
							opcodes.CALL_OPERATOR('_tmpVar2_3', '_tmpVar2_1', '+', '_tmpVar2_2'),
							opcodes.SET_VARIABLE('a', '_tmpVar2_3'),
							opcodes.RETURN('a')
						),
						None
					).obj,
				)
			}
		).obj,
		opcodes.CALL_FUNCTION('_tmpVar1', 'C'),
		opcodes.SET_VARIABLE('c', '_tmpVar1'),
		opcodes.GET_ATTRIBUTE('_tmpVar1', 'c', 'method'),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar2', Number.call.obj, args=['1']),
		opcodes.CALL_FUNCTION('_tmpVar3', '_tmpVar1', args=['_tmpVar2']),
		opcodes.SET_VARIABLE('tMethodResult', '_tmpVar3')
	]

	assert str(String.call.obj(execute.executed.scope['c']).obj) == "C<{'a': Number<1>}>"
	assert execute.executed.scope['tMethodResult'] == Number.call.obj('3').obj
