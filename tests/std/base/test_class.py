from unittest.mock import ANY, Mock

from actl import opcodes
from actl.objects import Number, Signature, String, PyToA, makeClass
from std.base.objects import Function
from std.base.objects.class_ import buildClass


ORDER_KEY = 9


async def test_simpleClassDeclare(execute):
	execute('class C:\n' '	a = 1')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			'C',
			buildClass.call,
			staticArgs=(
				'C',
				(),
				(
					opcodes.CALL_FUNCTION_STATIC(
						'_tmpVar1_1', function=Number.call, staticArgs=['1']
					),
					opcodes.SET_VARIABLE('a', '_tmpVar1_1'),
				),
			),
		)
	]

	cls = execute.executed.scope['C']
	assert cls == makeClass('C', (), extraAttributes={'a': await Number.call(1)})
	assert str(cls) == "class 'C'"
	assert str(await cls.call()) == 'C<>'


async def test_classWithInitMethod(execute):
	execute('class C:\n' '	fun __init__(self, a):\n' '		self.a = a\n' 'c = C(1)')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			'C',
			buildClass.call,
			staticArgs=(
				'C',
				(),
				(
					opcodes.CALL_FUNCTION_STATIC(
						'__init__',
						Function.call,
						staticArgs=(
							'__init__',
							await Signature.call(['self', 'a']),
							(
								opcodes.SET_ATTRIBUTE('self', 'a', 'a'),
								opcodes.RETURN('None'),
							),
						),
						kwargs={'scope': '__scope__'},
					),
				),
			),
		),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', Number.call, staticArgs=['1']),
		opcodes.CALL_FUNCTION('_tmpVar2', 'C', args=['_tmpVar1']),
		opcodes.SET_VARIABLE('c', '_tmpVar2'),
	]

	assert execute.executed.scope['C'] == makeClass(
		'C',
		(),
		self_={
			'__init__': await Function.call(
				'__init__',
				await Signature.call(['self', 'a']),
				(opcodes.SET_ATTRIBUTE('self', 'a', 'a'), opcodes.RETURN('None')),
				ANY,
			)
		},
	)
	assert str(await String.call(execute.executed.scope['c'])) == 'C<a=Number<1>>'


async def test_classWithMethod(execute):
	execute(
		'class C:\n'
		'	fun method(self, a):\n'
		'		self.a = a\n'
		'		a = self.a + 2\n'
		'		return a\n'
		'c = C()\n'
		'tMethodResult = c.method(1)'
	)

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			'C',
			buildClass.call,
			staticArgs=(
				'C',
				(),
				(
					opcodes.CALL_FUNCTION_STATIC(
						'method',
						Function.call,
						staticArgs=(
							'method',
							await Signature.call(['self', 'a']),
							(
								opcodes.SET_ATTRIBUTE('self', 'a', 'a'),
								opcodes.GET_ATTRIBUTE('_tmpVar2_1', 'self', 'a'),
								opcodes.CALL_FUNCTION_STATIC(
									'_tmpVar2_2', Number.call, staticArgs=['2']
								),
								opcodes.CALL_OPERATOR(
									'_tmpVar2_3', '_tmpVar2_1', '+', '_tmpVar2_2'
								),
								opcodes.SET_VARIABLE('a', '_tmpVar2_3'),
								opcodes.RETURN('a'),
							),
						),
						kwargs={'scope': '__scope__'},
					),
				),
			),
		),
		opcodes.CALL_FUNCTION('_tmpVar1', 'C'),
		opcodes.SET_VARIABLE('c', '_tmpVar1'),
		opcodes.GET_ATTRIBUTE('_tmpVar1', 'c', 'method'),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar2', Number.call, staticArgs=['1']),
		opcodes.CALL_FUNCTION('_tmpVar3', '_tmpVar1', args=['_tmpVar2']),
		opcodes.SET_VARIABLE('tMethodResult', '_tmpVar3'),
	]

	assert str(await String.call(execute.executed.scope['c'])) == 'C<a=Number<1>>'
	assert execute.executed.scope['tMethodResult'] == await Number.call('3')


async def test_classWithTwoMethod(execute):
	execute(
		'class C:\n'
		'	fun methodA(self, a):\n'
		'		self.a = a\n'
		'		a = self.a + 2\n'
		'		return a\n'
		'\n'
		'	fun methodB(self, b):\n'
		'		b = b + 1\n'
		'		return self.methodA(b)\n'
		'\n'
		'c = C()\n'
		'tMethodResult = c.methodB(1)'
	)

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			'C',
			buildClass.call,
			staticArgs=(
				'C',
				(),
				(
					opcodes.CALL_FUNCTION_STATIC(
						'methodA',
						Function.call,
						staticArgs=(
							'methodA',
							await Signature.call(['self', 'a']),
							(
								opcodes.SET_ATTRIBUTE('self', 'a', 'a'),
								opcodes.GET_ATTRIBUTE('_tmpVar2_1', 'self', 'a'),
								opcodes.CALL_FUNCTION_STATIC(
									'_tmpVar2_2', Number.call, staticArgs=['2']
								),
								opcodes.CALL_OPERATOR(
									'_tmpVar2_3', '_tmpVar2_1', '+', '_tmpVar2_2'
								),
								opcodes.SET_VARIABLE('a', '_tmpVar2_3'),
								opcodes.RETURN('a'),
							),
						),
						kwargs={'scope': '__scope__'},
					),
					opcodes.CALL_FUNCTION_STATIC(
						'methodB',
						Function.call,
						staticArgs=(
							'methodB',
							await Signature.call(['self', 'b']),
							(
								opcodes.CALL_FUNCTION_STATIC(
									'_tmpVar2_1', Number.call, staticArgs=['1']
								),
								opcodes.CALL_OPERATOR(
									'_tmpVar2_2', 'b', '+', '_tmpVar2_1'
								),
								opcodes.SET_VARIABLE('b', '_tmpVar2_2'),
								opcodes.GET_ATTRIBUTE('_tmpVar2_3', 'self', 'methodA'),
								opcodes.CALL_FUNCTION(
									'_tmpVar2_4', '_tmpVar2_3', args=['b']
								),
								opcodes.RETURN('_tmpVar2_4'),
							),
						),
						kwargs={'scope': '__scope__'},
					),
				),
			),
		),
		opcodes.CALL_FUNCTION('_tmpVar1', 'C'),
		opcodes.SET_VARIABLE('c', '_tmpVar1'),
		opcodes.GET_ATTRIBUTE('_tmpVar1', 'c', 'methodB'),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar2', Number.call, staticArgs=['1']),
		opcodes.CALL_FUNCTION('_tmpVar3', '_tmpVar1', args=['_tmpVar2']),
		opcodes.SET_VARIABLE('tMethodResult', '_tmpVar3'),
	]

	assert str(execute.executed.scope['c']) == 'C<a=Number<2>>'
	assert str(execute.executed.scope['tMethodResult']) == 'Number<4>'


async def test_classInherit(execute):
	mock = Mock()
	execute.scope['mock'] = await PyToA.call(mock)

	execute('class Base:\n' '	fun baseMethod(self):\n' '		mock(1)\n')

	assert execute.executed
	execute.flush()
	execute(
		'class Inherit(Base):\n'
		'	fun inheritMerhod(self):\n'
		'		mock(2)\n'
		'\n'
		'inherit = Inherit()\n'
		'inherit.baseMethod()\n'
		'inherit.inheritMerhod()\n'
	)

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			'Inherit',
			buildClass.call,
			staticArgs=(
				'Inherit',
				(execute.parsed.scope['Base'],),
				(
					opcodes.CALL_FUNCTION_STATIC(
						'inheritMerhod',
						Function.call,
						staticArgs=(
							'inheritMerhod',
							await Signature.call(['self']),
							(
								opcodes.CALL_FUNCTION_STATIC(
									'_tmpVar2_1', Number.call, staticArgs=['2']
								),
								opcodes.CALL_FUNCTION(
									'_tmpVar2_2', 'mock', args=['_tmpVar2_1']
								),
								opcodes.VARIABLE('_tmpVar2_2'),
								opcodes.RETURN('None'),
							),
						),
						kwargs={'scope': '__scope__'},
					),
				),
			),
		),
		opcodes.CALL_FUNCTION('_tmpVar1', 'Inherit'),
		opcodes.SET_VARIABLE('inherit', '_tmpVar1'),
		opcodes.GET_ATTRIBUTE('_tmpVar1', 'inherit', 'baseMethod'),
		opcodes.CALL_FUNCTION('_tmpVar2', '_tmpVar1'),
		opcodes.VARIABLE('_tmpVar2'),
		opcodes.GET_ATTRIBUTE('_tmpVar1', 'inherit', 'inheritMerhod'),
		opcodes.CALL_FUNCTION(
			'_tmpVar2',
			'_tmpVar1',
		),
		opcodes.VARIABLE('_tmpVar2'),
	]

	assert execute.executed.scope['inherit']
	assert mock.call_args_list == [((1,),), ((2,),)]
