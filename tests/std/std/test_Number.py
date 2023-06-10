from actl import opcodes, objects


ORDER_KEY = 1


async def test_Number(execute):
	execute('1')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1',
			function='Number',
			staticArgs=[await objects.PyToA.call('1')],
		),
		opcodes.VARIABLE(name='_tmpVar1'),
	]
	assert str(execute.executed.scope['_tmpVar1']) == 'Number<_head=PyToA<1>>'


async def test_floatNumber(execute):
	execute('1.1')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1',
			function='Number',
			staticArgs=[await objects.PyToA.call('1.1')],
		),
		opcodes.VARIABLE(name='_tmpVar1'),
	]
	assert str(execute.executed.scope['_tmpVar1']) == 'Number<_head=PyToA<1.1>>'


async def test_negativeNumber(execute):
	execute('-1')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1',
			function='Number',
			staticArgs=[await objects.PyToA.call('-1')],
		),
		opcodes.VARIABLE(name='_tmpVar1'),
	]
	assert str(execute.executed.scope['_tmpVar1']) == 'Number<_head=PyToA<-1>>'
