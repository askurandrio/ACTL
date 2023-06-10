from actl import opcodes
from actl.Buffer import Buffer
from actl.objects import AToPy
from std.base.objects import If


ORDER_KEY = 3


async def test_simple_if(execute):
	execute('if "a": a = "a"')

	assert execute.parsed.code == [
		await If.call(
			(
				(
					opcodes.CALL_FUNCTION_STATIC(
						dst='_tmpVar1', function='String', staticArgs=['a']
					),
					opcodes.VARIABLE(name='_tmpVar1'),
				),
				(
					opcodes.CALL_FUNCTION_STATIC(
						dst='_tmpVar2', function='String', staticArgs=['a']
					),
					opcodes.SET_VARIABLE(dst='a', src='_tmpVar2'),
				),
			)
		)
	]
	assert AToPy(execute.executed.scope['a']) == 'a'


async def test_ifFalse(execute):
	execute('if "": a = "a"')

	if_ = execute.parsed.code.one()
	assert (await if_.getAttribute('__class__')) is If
	conditionFrame, code = Buffer(await if_.getAttribute('conditions')).one()
	assert conditionFrame == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1', function='String', staticArgs=['']
		),
		opcodes.VARIABLE(name='_tmpVar1'),
	)
	assert code == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar2', function='String', staticArgs=['a']
		),
		opcodes.SET_VARIABLE(dst='a', src='_tmpVar2'),
	)

	assert 'a' not in execute.executed.scope


async def test_ifElif(execute):
	execute('if "": a = "a" elif "a": a = "b"')

	if_ = execute.parsed.code.one()
	assert await if_.getAttribute('__class__') is If
	assert await if_.getAttribute('conditions') == (
		(
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='_tmpVar1', function='String', staticArgs=['']
				),
				opcodes.VARIABLE(name='_tmpVar1'),
			),
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='_tmpVar2', function='String', staticArgs=['a']
				),
				opcodes.SET_VARIABLE(dst='a', src='_tmpVar2'),
			),
		),
		(
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='_tmpVar3', function='String', staticArgs=['a']
				),
				opcodes.VARIABLE(name='_tmpVar3'),
			),
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='_tmpVar4', function='String', staticArgs=['b']
				),
				opcodes.SET_VARIABLE(dst='a', src='_tmpVar4'),
			),
		),
	)
	assert AToPy(execute.executed.scope['a']) == 'b'


async def test_ifElse(execute):
	execute('if "": a = "a" else: a = "b"')

	if_ = execute.parsed.code.one()
	assert await if_.getAttribute('__class__') is If
	conditionFrame, code = Buffer(await if_.getAttribute('conditions')).one()
	assert conditionFrame == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar1', function='String', staticArgs=['']
		),
		opcodes.VARIABLE(name='_tmpVar1'),
	)
	assert code == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar2', function='String', staticArgs=['a']
		),
		opcodes.SET_VARIABLE(dst='a', src='_tmpVar2'),
	)
	assert await if_.getAttribute('elseCode') == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar3', function='String', staticArgs=['b']
		),
		opcodes.SET_VARIABLE(dst='a', src='_tmpVar3'),
	)
	assert AToPy(execute.executed.scope['a']) == 'b'


async def test_ifElifElseWithFullCodeBlock(execute):
	execute('if "":\n a = "a"\nelif "":\n a = "b"\nelse:\n a = "c"')

	if_ = execute.parsed.code.one()
	assert await if_.getAttribute('__class__') is If
	assert await if_.getAttribute('conditions') == (
		(
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='_tmpVar1', function='String', staticArgs=['']
				),
				opcodes.VARIABLE(name='_tmpVar1'),
			),
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='_tmpVar2', function='String', staticArgs=['a']
				),
				opcodes.SET_VARIABLE(dst='a', src='_tmpVar2'),
			),
		),
		(
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='_tmpVar3', function='String', staticArgs=['']
				),
				opcodes.VARIABLE(name='_tmpVar3'),
			),
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='_tmpVar4', function='String', staticArgs=['b']
				),
				opcodes.SET_VARIABLE(dst='a', src='_tmpVar4'),
			),
		),
	)
	assert await if_.getAttribute('elseCode') == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='_tmpVar5', function='String', staticArgs=['c']
		),
		opcodes.SET_VARIABLE(dst='a', src='_tmpVar5'),
	)
	assert AToPy(execute.executed.scope['a']) == 'c'
