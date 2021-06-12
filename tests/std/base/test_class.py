from unittest.mock import ANY

from actl import opcodes
from actl.objects import Number, Signature, String
from std.base.objects import class_, Function


ORDER_KEY = 9


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


def test_classWithInitMethod(execute):
	execute(
		'class C:\n'
		'    fun __init__(self, a):\n'
		'        self.a = a\n'
		'c = C(1)'
	)

	assert execute.parsed.code == [
		class_.call(
			'C',
			{
				'body': (
					Function.call(
						'__init__',
						Signature.call(['self', 'a']),
						(
							opcodes.SET_ATTRIBUTE('self', 'a', 'a'),
							opcodes.RETURN('None')
						),
						None
					),
				)
			}
		),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', Number.call, args=['1']),
		opcodes.CALL_FUNCTION('_tmpVar2', 'C', args=['_tmpVar1']),
		opcodes.SET_VARIABLE('c', '_tmpVar2')
	]

	assert execute.executed.scope['C'] == class_.call(
		'C',
		{
			'__self__': {
				'__init__': Function.call(
					'__init__',
					Signature.call(['self', 'a']),
					(
						opcodes.SET_ATTRIBUTE('self', 'a', 'a'),
						opcodes.RETURN('None')
					),
					ANY
				)
			}
		}
	)
	assert str(String.call(execute.executed.scope['c'])) == 'C<a=Number<1>>'


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
		class_.call(
			'C',
			{
				'body': (
					Function.call(
						'method',
						Signature.call(['self', 'a']),
						(
							opcodes.SET_ATTRIBUTE('self', 'a', 'a'),
							opcodes.GET_ATTRIBUTE('_tmpVar2_1', 'self', 'a'),
							opcodes.CALL_FUNCTION_STATIC('_tmpVar2_2', Number.call, args=['2']),
							opcodes.CALL_OPERATOR('_tmpVar2_3', '_tmpVar2_1', '+', '_tmpVar2_2'),
							opcodes.SET_VARIABLE('a', '_tmpVar2_3'),
							opcodes.RETURN('a')
						),
						None
					),
				)
			}
		),
		opcodes.CALL_FUNCTION('_tmpVar1', 'C'),
		opcodes.SET_VARIABLE('c', '_tmpVar1'),
		opcodes.GET_ATTRIBUTE('_tmpVar1', 'c', 'method'),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar2', Number.call, args=['1']),
		opcodes.CALL_FUNCTION('_tmpVar3', '_tmpVar1', args=['_tmpVar2']),
		opcodes.SET_VARIABLE('tMethodResult', '_tmpVar3')
	]

	assert str(String.call(execute.executed.scope['c'])) == 'C<a=Number<1>>'
	assert execute.executed.scope['tMethodResult'] == Number.call('3')


def test_classWithTwoMethod(execute):
	execute(
		'class C:\n'
		'    fun methodA(self, a):\n'
		'        self.a = a\n'
	   '        a = self.a + 2\n'
		'        return a\n'
		'\n'
		'    fun methodB(self, b):\n'
		'        b = b + 1\n'
		'        return self.methodA(b)\n'
		'\n'
		'c = C()\n'
		'tMethodResult = c.methodB(1)'
	)

	assert execute.parsed.code == [
		class_.call(
			'C',
			{
				'body': (
					Function.call(
						'methodA',
						Signature.call(['self', 'a']),
						(
							opcodes.SET_ATTRIBUTE('self', 'a', 'a'),
							opcodes.GET_ATTRIBUTE('_tmpVar2_1', 'self', 'a'),
							opcodes.CALL_FUNCTION_STATIC('_tmpVar2_2', Number.call, args=['2']),
							opcodes.CALL_OPERATOR('_tmpVar2_3', '_tmpVar2_1', '+', '_tmpVar2_2'),
							opcodes.SET_VARIABLE('a', '_tmpVar2_3'),
							opcodes.RETURN('a')
						),
						None
					),
					Function.call(
						'methodB',
						Signature.call(['self', 'b']),
						(
							opcodes.CALL_FUNCTION_STATIC('_tmpVar2_1', Number.call, args=['1']),
							opcodes.CALL_OPERATOR('_tmpVar2_2', 'b', '+', '_tmpVar2_1'),
							opcodes.SET_VARIABLE('b', '_tmpVar2_2'),
							opcodes.GET_ATTRIBUTE('_tmpVar2_3', 'self', 'methodA'),
							opcodes.CALL_FUNCTION('_tmpVar2_4', '_tmpVar2_3', args=['b']),
							opcodes.RETURN('_tmpVar2_4')
						),
						None
					)
				),

			}
		),
		opcodes.CALL_FUNCTION('_tmpVar1', 'C'),
		opcodes.SET_VARIABLE('c', '_tmpVar1'),
		opcodes.GET_ATTRIBUTE('_tmpVar1', 'c', 'methodB'),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar2', Number.call, args=['1']),
		opcodes.CALL_FUNCTION('_tmpVar3', '_tmpVar1', args=['_tmpVar2']),
		opcodes.SET_VARIABLE('tMethodResult', '_tmpVar3')
	]

	assert str(execute.executed.scope['c']) == 'C<a=Number<2>>'
	assert str(execute.executed.scope['tMethodResult']) == 'Number<4>'
