from unittest.mock import ANY, Mock

from actl import opcodes
from actl.objects import Signature, String, PyToA, class_
from std.base.objects import Function
from std.base.objects.class_ import buildClass


ORDER_KEY = 9


async def test_simpleClassDeclare(execute):
	execute('class C:\n	a = "a"')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			'C',
			buildClass.call,
			staticArgs=(
				'C',
				(),
				(
					opcodes.CALL_FUNCTION_STATIC(
						'#1_1', function='String', staticArgs=['a']
					),
					opcodes.SET_VARIABLE('a', '#1_1'),
				),
			),
		)
	]

	cls = execute.executed.scope['C']
	assert cls == await class_.call(
		'C', (), extraAttributes={'a': await String.call('a')}
	)
	assert str(cls) == "class 'C'"
	assert str(await cls.call()) == 'C<>'


async def test_classWithInitMethod(execute):
	execute('class C:\n	fun __init__(self, a):\n		self.a = a\nc = C("a")')

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
							await Signature.call(('self', 'a')),
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
		opcodes.CALL_FUNCTION_STATIC('#1', 'String', staticArgs=['a']),
		opcodes.CALL_FUNCTION('#2', 'C', args=['#1']),
		opcodes.SET_VARIABLE('c', '#2'),
	]

	assert (
		await class_.call(
			'C',
			(),
			self_={
				'__init__': await Function.call(
					'__init__',
					await Signature.call(('self', 'a')),
					(opcodes.SET_ATTRIBUTE('self', 'a', 'a'), opcodes.RETURN('None')),
					ANY,
				)
			},
		)
		== execute.executed.scope['C']
	)

	assert str(await String.call(execute.executed.scope['c'])) == 'C<a=a>'


# async def test_classWithMethod(execute):
# 	execute(
# 		'class C:\n'
# 		'	fun method(self, a):\n'
# 		'		self.a = a\n'
# 		'		a = self.a + 2\n'
# 		'		return a\n'
# 		'c = C()\n'
# 		'tMethodResult = c.method(1)'
# 	)

# 	assert execute.parsed.code == [
# 		opcodes.CALL_FUNCTION_STATIC(
# 			'C',
# 			buildClass.call,
# 			staticArgs=(
# 				'C',
# 				(),
# 				(
# 					opcodes.CALL_FUNCTION_STATIC(
# 						'method',
# 						Function.call,
# 						staticArgs=(
# 							'method',
# 							await Signature.call(('self', 'a')),
# 							(
# 								opcodes.SET_ATTRIBUTE('self', 'a', 'a'),
# 								opcodes.GET_ATTRIBUTE('#2_1', 'self', 'a'),
# 								opcodes.CALL_FUNCTION_STATIC(
# 									'#2_2', 'String', staticArgs=['2']
# 								),
# 								opcodes.CALL_OPERATOR(
# 									'#2_3', '#2_1', '+', '#2_2'
# 								),
# 								opcodes.SET_VARIABLE('a', '#2_3'),
# 								opcodes.RETURN('a'),
# 							),
# 						),
# 						kwargs={'scope': '__scope__'},
# 					),
# 				),
# 			),
# 		),
# 		opcodes.CALL_FUNCTION('#1', 'C'),
# 		opcodes.SET_VARIABLE('c', '#1'),
# 		opcodes.GET_ATTRIBUTE('#1', 'c', 'method'),
# 		opcodes.CALL_FUNCTION_STATIC('#2', Number.call, staticArgs=['1']),
# 		opcodes.CALL_FUNCTION('#3', '#1', args=['#2']),
# 		opcodes.SET_VARIABLE('tMethodResult', '#3'),
# 	]

# 	assert str(await String.call(execute.executed.scope['c'])) == 'C<a=Number<1>>'
# 	assert execute.executed.scope['tMethodResult'] == await Number.call('3')


# async def test_classWithTwoMethod(execute):
# 	execute(
# 		'class C:\n'
# 		'	fun methodA(self, a):\n'
# 		'		self.a = a\n'
# 		'		a = self.a + 2\n'
# 		'		return a\n'
# 		'\n'
# 		'	fun methodB(self, b):\n'
# 		'		b = b + 1\n'
# 		'		return self.methodA(b)\n'
# 		'\n'
# 		'c = C()\n'
# 		'tMethodResult = c.methodB(1)'
# 	)

# 	assert execute.parsed.code == [
# 		opcodes.CALL_FUNCTION_STATIC(
# 			'C',
# 			buildClass.call,
# 			staticArgs=(
# 				'C',
# 				(),
# 				(
# 					opcodes.CALL_FUNCTION_STATIC(
# 						'methodA',
# 						Function.call,
# 						staticArgs=(
# 							'methodA',
# 							await Signature.call(('self', 'a')),
# 							(
# 								opcodes.SET_ATTRIBUTE('self', 'a', 'a'),
# 								opcodes.GET_ATTRIBUTE('#2_1', 'self', 'a'),
# 								opcodes.CALL_FUNCTION_STATIC(
# 									'#2_2', Number.call, staticArgs=['2']
# 								),
# 								opcodes.CALL_OPERATOR(
# 									'#2_3', '#2_1', '+', '#2_2'
# 								),
# 								opcodes.SET_VARIABLE('a', '#2_3'),
# 								opcodes.RETURN('a'),
# 							),
# 						),
# 						kwargs={'scope': '__scope__'},
# 					),
# 					opcodes.CALL_FUNCTION_STATIC(
# 						'methodB',
# 						Function.call,
# 						staticArgs=(
# 							'methodB',
# 							await Signature.call(('self', 'b')),
# 							(
# 								opcodes.CALL_FUNCTION_STATIC(
# 									'#2_1', Number.call, staticArgs=['1']
# 								),
# 								opcodes.CALL_OPERATOR(
# 									'#2_2', 'b', '+', '#2_1'
# 								),
# 								opcodes.SET_VARIABLE('b', '#2_2'),
# 								opcodes.GET_ATTRIBUTE('#2_3', 'self', 'methodA'),
# 								opcodes.CALL_FUNCTION(
# 									'#2_4', '#2_3', args=['b']
# 								),
# 								opcodes.RETURN('#2_4'),
# 							),
# 						),
# 						kwargs={'scope': '__scope__'},
# 					),
# 				),
# 			),
# 		),
# 		opcodes.CALL_FUNCTION('#1', 'C'),
# 		opcodes.SET_VARIABLE('c', '#1'),
# 		opcodes.GET_ATTRIBUTE('#1', 'c', 'methodB'),
# 		opcodes.CALL_FUNCTION_STATIC('#2', Number.call, staticArgs=['1']),
# 		opcodes.CALL_FUNCTION('#3', '#1', args=['#2']),
# 		opcodes.SET_VARIABLE('tMethodResult', '#3'),
# 	]

# 	assert str(execute.executed.scope['c']) == 'C<a=Number<2>>'
# 	assert str(execute.executed.scope['tMethodResult']) == 'Number<4>'


async def test_classInherit(execute):
	mock = Mock()
	execute.scope['mock'] = await PyToA.call(mock)

	execute('class Base:\n	fun baseMethod(self):\n		mock("a")\n')

	assert execute.executed
	execute.flush()
	execute(
		'class Inherit(Base):\n'
		'	fun inheritMerhod(self):\n'
		'		mock("b")\n'
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
							await Signature.call(('self',)),
							(
								opcodes.CALL_FUNCTION_STATIC(
									'#2_1', 'String', staticArgs=['b']
								),
								opcodes.CALL_FUNCTION('#2_2', 'mock', args=['#2_1']),
								opcodes.VARIABLE('#2_2'),
								opcodes.RETURN('None'),
							),
						),
						kwargs={'scope': '__scope__'},
					),
				),
			),
		),
		opcodes.CALL_FUNCTION('#1', 'Inherit'),
		opcodes.SET_VARIABLE('inherit', '#1'),
		opcodes.GET_ATTRIBUTE('#1', 'inherit', 'baseMethod'),
		opcodes.CALL_FUNCTION('#2', '#1'),
		opcodes.VARIABLE('#2'),
		opcodes.GET_ATTRIBUTE('#1', 'inherit', 'inheritMerhod'),
		opcodes.CALL_FUNCTION('#2', '#1'),
		opcodes.VARIABLE('#2'),
	]

	assert execute.executed.scope['inherit']
	assert mock.call_args_list == [(('a',),), (('b',),)]
