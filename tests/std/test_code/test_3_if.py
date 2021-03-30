from actl import opcodes
from actl.Buffer import Buffer
from actl.objects import AToPy, Number
from std.objects import If


def test_if(execute):
	execute('if 1: a = 2')

	if_ = execute.parsed.code.one()
	assert if_.getAttribute('__class__') is If
	conditionFrame, code = Buffer(if_.getAttribute('conditions')).one()
	assert conditionFrame == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function=Number.call, args=['1']
		),
		opcodes.VARIABLE(name='__IV11')
	)
	assert code == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV12', function=Number.call, args=['2']
		),
		opcodes.SET_VARIABLE(dst='a', src='__IV12')
	)

	assert AToPy(execute.executed.scope['a']) == 2


def test_ifFalse(execute):
	execute('if 0: a = 1')

	if_ = execute.parsed.code.one()
	assert if_.getAttribute('__class__') is If
	conditionFrame, code = Buffer(if_.getAttribute('conditions')).one()
	assert conditionFrame == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function=Number.call, args=['0']
		),
		opcodes.VARIABLE(name='__IV11')
	)
	assert code == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV12', function=Number.call, args=['1']
		),
		opcodes.SET_VARIABLE(dst='a', src='__IV12')
	)

	assert not AToPy(execute.executed.scope['_'])


def test_ifElif(execute):
	execute('if 0: a = 1 elif 1: a = 2')

	if_ = execute.parsed.code.one()
	assert if_.getAttribute('__class__') is If
	assert if_.getAttribute('conditions') == (
		(
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='__IV11', function=Number.call, args=['0']
				),
				opcodes.VARIABLE(name='__IV11')
			),
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='__IV12', function=Number.call, args=['1']
				),
				opcodes.SET_VARIABLE(dst='a', src='__IV12')
			)
		),
		(
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='__IV13', function=Number.call, args=['1']
				),
				opcodes.VARIABLE(name='__IV13')
			),
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='__IV14', function=Number.call, args=['2']
				),
				opcodes.SET_VARIABLE(dst='a', src='__IV14')
			)
		)
	)
	assert AToPy(execute.executed.scope['a']) == 2


def test_ifElse(execute):
	execute('if 0: a = 1 else: a = 2')

	if_ = execute.parsed.code.one()
	assert if_.getAttribute('__class__') is If
	conditionFrame, code = Buffer(if_.getAttribute('conditions')).one()
	assert conditionFrame == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function=Number.call, args=['0']
		),
		opcodes.VARIABLE(name='__IV11')
	)
	assert code == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV12', function=Number.call, args=['1']
		),
		opcodes.SET_VARIABLE(dst='a', src='__IV12')
	)
	assert if_.getAttribute('elseCode') == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV13', function=Number.call, args=['2']
		),
		opcodes.SET_VARIABLE(dst='a', src='__IV13')
	)
	assert AToPy(execute.executed.scope['a']) == 2


def test_ifElifElseWithFullCodeBlock(execute):
	execute('if 0:\n a = 1\nelif 0:\n a = 2\nelse:\n a = 3')

	if_ = execute.parsed.code.one()
	assert if_.getAttribute('__class__') is If
	assert if_.getAttribute('conditions') == (
		(
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='__IV11', function=Number.call, args=['0']
				),
				opcodes.VARIABLE(name='__IV11')
			),
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='__IV12', function=Number.call, args=['1']
				),
				opcodes.SET_VARIABLE(dst='a', src='__IV12')
			)
		),
		(
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='__IV13', function=Number.call, args=['0']
				),
				opcodes.VARIABLE(name='__IV13')
			),
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='__IV14', function=Number.call, args=['2']
				),
				opcodes.SET_VARIABLE(dst='a', src='__IV14')
			)
		)
	)
	assert if_.getAttribute('elseCode') == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV15', function=Number.call, args=['3']
		),
		opcodes.SET_VARIABLE(dst='a', src='__IV15')
	)
	assert AToPy(execute.executed.scope['a']) == 3
