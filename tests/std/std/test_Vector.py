import pytest

from actl import opcodes

from std.std.rules import vector__of


ORDER_KEY = 1


def test_Vector__init(execute):
	execute('v = Vector()\n')

	assert str(execute.executed.scope['v']) == 'Vector<_head=[]>'


def test_Vector__append(execute):
	execute('v = Vector()\nv.append("a")')

	assert str(execute.executed.scope['v']) == 'Vector<_head=[a]>'


async def test_Vector_syntaxInit(execute):
	execute('[]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1', function='Vector'),
		opcodes.VARIABLE(name='_tmpVar1'),
	]
	vector = execute.executed.scope['_tmpVar1']
	assert await vector.getAttribute('__class__') is execute.scope['Vector']


async def test_Vector_syntaxInitWithNumber(execute):
	execute('["a"]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', 'Vector'),
		opcodes.GET_ATTRIBUTE('_tmpVar2', '_tmpVar1', 'append'),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar4', "String", staticArgs=['a']),
		opcodes.CALL_FUNCTION('_tmpVar3', '_tmpVar2', args=['_tmpVar4']),
		opcodes.VARIABLE(name='_tmpVar1'),
	]
	vector = execute.executed.scope['_tmpVar1']
	assert await vector.getAttribute('__class__') is execute.scope['Vector']


@pytest.mark.parametrize("length", list(range(2, 6)))
async def test_ConstVector_syntaxInit(execute, length):
	execute(', '.join(f'"{idx}"' for idx in range(length)))

	assert execute.parsed.code == [
		*[
			opcodes.CALL_FUNCTION_STATIC(
				f'_tmpVar{index + 1}', 'String', staticArgs=[str(index)]
			)
			for index in range(length)
		],
		opcodes.CALL_FUNCTION_STATIC(
			f'_tmpVar{length + 1}',
			vector__of.call,
			args=[f'_tmpVar{index + 1}' for index in range(length)],
		),
		opcodes.VARIABLE(f'_tmpVar{length + 1}'),
	]

	headAsStr = ', '.join(map(str, range(length)))
	assert (
		str(execute.executed.scope[f'_tmpVar{length + 1}'])
		== f'Vector<_head=[{headAsStr}]>'
	)


@pytest.mark.parametrize("length", list(range(2, 6)))
async def test_ConstVector_packUnpack(execute, length):
	setCode = ', '.join(f'"{idx}"' for idx in range(length))
	getCode = ', '.join(f'v{index}' for index in range(length))
	execute(f'v = {setCode}\n{getCode} = v')

	assert execute.parsed.code == [
		*[
			opcodes.CALL_FUNCTION_STATIC(
				f'_tmpVar{index + 1}', 'String', staticArgs=[str(index)]
			)
			for index in range(length)
		],
		opcodes.CALL_FUNCTION_STATIC(
			f'_tmpVar{length + 1}',
			vector__of.call,
			args=[f'_tmpVar{index + 1}' for index in range(length)],
		),
		opcodes.SET_VARIABLE('v', f'_tmpVar{length + 1}'),
		opcodes.CALL_FUNCTION('_tmpVar1_1', 'Iter', args=['v']),
		opcodes.GET_ATTRIBUTE('_tmpVar1_2', '_tmpVar1_1', 'next'),
		*[opcodes.CALL_FUNCTION(f'v{index}', '_tmpVar1_2') for index in range(length)],
	]

	for index in range(length):
		assert str(execute.executed.scope[f'v{index}']) == str(index)
