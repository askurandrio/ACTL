import pytest

from actl import opcodes

from std.std.rules import vector__of


ORDER_KEY = 2


def test_Vector__init(execute):
	execute('v = Vector()\n')

	assert str(execute.executed.scope['v']) == 'Vector<_head=PyToA<[]>>'


def test_Vector__append(execute):
	execute('v = Vector()\nv.append("a")')

	assert str(execute.executed.scope['v']) == 'Vector<_head=PyToA<[a]>>'


async def test_Vector_syntaxInit(execute):
	execute('[]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='#1', function='Vector'),
		opcodes.VARIABLE(name='#1'),
	]
	vector = execute.executed.scope['#1']
	assert await vector.getAttribute('__class__') is execute.scope['Vector']


async def test_Vector_syntaxInitWithNumber(execute):
	execute('["a"]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC('#1', 'Vector'),
		opcodes.GET_ATTRIBUTE('#2', '#1', 'append'),
		opcodes.CALL_FUNCTION_STATIC('#4', "String", staticArgs=['a']),
		opcodes.CALL_FUNCTION('#3', '#2', args=['#4']),
		opcodes.VARIABLE(name='#1'),
	]
	vector = execute.executed.scope['#1']
	assert await vector.getAttribute('__class__') is execute.scope['Vector']


@pytest.mark.parametrize("length", list(range(2, 6)))
async def test_ConstVector_syntaxInitMultipleItems(execute, length):
	execute(', '.join(f'"{idx}"' for idx in range(length)))

	assert execute.parsed.code == [
		*[
			opcodes.CALL_FUNCTION_STATIC(
				f'#{index + 1}', 'String', staticArgs=[str(index)]
			)
			for index in range(length)
		],
		opcodes.CALL_FUNCTION_STATIC(
			f'#{length + 1}',
			vector__of.call,
			args=[f'#{index + 1}' for index in range(length)],
		),
		opcodes.VARIABLE(f'#{length + 1}'),
	]

	headAsStr = ', '.join(map(str, range(length)))
	assert (
		str(execute.executed.scope[f'#{length + 1}'])
		== f'Vector<_head=PyToA<[{headAsStr}]>>'
	)


@pytest.mark.parametrize("length", list(range(2, 6)))
async def test_ConstVector_packUnpack(execute, length):
	setCode = ', '.join(f'"{idx}"' for idx in range(length))
	getCode = ', '.join(f'v{index}' for index in range(length))
	execute(f'{getCode} = {setCode}')

	assert execute.parsed.code == [
		*[
			opcodes.CALL_FUNCTION_STATIC(
				f'#{index + 1}', 'String', staticArgs=[str(index)]
			)
			for index in range(length)
		],
		opcodes.CALL_FUNCTION_STATIC(
			f'#{length + 1}',
			vector__of.call,
			args=[f'#{index + 1}' for index in range(length)],
		),
		opcodes.CALL_FUNCTION('#1_1', 'Iter', args=[f'#{length + 1}']),
		opcodes.GET_ATTRIBUTE('#1_2', '#1_1', 'next'),
		*[opcodes.CALL_FUNCTION(f'v{index}', '#1_2') for index in range(length)],
	]

	for index in range(length):
		assert str(execute.executed.scope[f'v{index}']) == str(index)


@pytest.mark.parametrize("length", list(range(2, 6)))
async def test_ConstVector_packUnpackViaVariable(execute, length):
	setCode = ', '.join(f'"{idx}"' for idx in range(length))
	getCode = ', '.join(f'v{index}' for index in range(length))
	execute(f'v = {setCode}\n{getCode} = v')

	assert execute.parsed.code == [
		*[
			opcodes.CALL_FUNCTION_STATIC(
				f'#{index + 1}', 'String', staticArgs=[str(index)]
			)
			for index in range(length)
		],
		opcodes.CALL_FUNCTION_STATIC(
			f'#{length + 1}',
			vector__of.call,
			args=[f'#{index + 1}' for index in range(length)],
		),
		opcodes.SET_VARIABLE('v', f'#{length + 1}'),
		opcodes.CALL_FUNCTION('#1_1', 'Iter', args=['v']),
		opcodes.GET_ATTRIBUTE('#1_2', '#1_1', 'next'),
		*[opcodes.CALL_FUNCTION(f'v{index}', '#1_2') for index in range(length)],
	]

	for index in range(length):
		assert str(execute.executed.scope[f'v{index}']) == str(index)
