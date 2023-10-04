from actl import opcodes


ORDER_KEY = 7


async def test_pointOperator(execute):
	execute('print.__call__')

	assert execute.parsed.code == [
		opcodes.GET_ATTRIBUTE('#1', 'print', '__call__'),
		opcodes.VARIABLE(name='#1'),
	]

	assert execute.executed.scope['#1'] == await execute.scope['print'].getAttribute(
		'__call__'
	)


# async def test_add(execute):
# 	execute('1 + 2')

# 	assert execute.parsed.code == [
# 		opcodes.CALL_FUNCTION_STATIC(
# 			dst='#1', function=Number.call, staticArgs=['1']
# 		),
# 		opcodes.CALL_FUNCTION_STATIC(
# 			dst='#2', function=Number.call, staticArgs=['2']
# 		),
# 		opcodes.CALL_OPERATOR(
# 			dst='#3', first='#1', operator='+', second='#2'
# 		),
# 		opcodes.VARIABLE(name='#3'),
# 	]

# 	assert execute.executed.scope['#3'] == await Number.call('3')


# async def test_setAddResult(execute):
# 	execute('a = 1 + 2')

# 	assert execute.parsed.code == [
# 		opcodes.CALL_FUNCTION_STATIC(
# 			dst='#1', function=Number.call, staticArgs=['1']
# 		),
# 		opcodes.CALL_FUNCTION_STATIC(
# 			dst='#2', function=Number.call, staticArgs=['2']
# 		),
# 		opcodes.CALL_OPERATOR(
# 			dst='#3', first='#1', operator='+', second='#2'
# 		),
# 		opcodes.SET_VARIABLE('a', '#3'),
# 	]

# 	assert execute.executed.scope['a'] == await Number.call('3')
