import pytest

from actl import opcodes
from actl.objects import Number

from std._std.rules import vector__of


ORDER_KEY = 1


def test_Vector__init(execute):
	execute.executeInInitialScope('from std._std.objects.vector.vector import Vector')
	execute.executeInInitialScope('import std._std.objects.vector.vector__init')

	execute('v = Vector()\n')

	assert str(execute.executed.scope['v']) == 'Vector<_head=[]>'


def test_Vector__append(execute):
	execute.executeInInitialScope('from std._std.objects.vector.vector import Vector')
	execute.executeInInitialScope('import std._std.objects.vector.vector__init')
	execute.executeInInitialScope('import std._std.objects.vector.vector__append')

	execute('v = Vector()\nv.append(1)')

	assert str(execute.executed.scope['v']) == 'Vector<_head=[1]>'


async def test_Vector_syntaxInit(execute):
	execute.executeInInitialScope('from std._std.objects.vector.vector import Vector')
	execute.executeInInitialScope('import std._std.objects.vector.vector__init')

	execute('[]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='_tmpVar1', function='Vector'),
		opcodes.VARIABLE(name='_tmpVar1'),
	]
	vector = execute.executed.scope['_tmpVar1']
	assert await vector.getAttribute('__class__') is execute.scope['Vector']


async def test_Vector_syntaxInitWithNumber(execute):
	execute.executeInInitialScope('from std._std.objects.vector.vector import Vector')
	execute.executeInInitialScope('import std._std.objects.vector.vector__init')
	execute.executeInInitialScope('import std._std.objects.vector.vector__append')

	execute('[1]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', 'Vector'),
		opcodes.GET_ATTRIBUTE('_tmpVar2', '_tmpVar1', 'append'),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar4', Number.call, staticArgs=['1']),
		opcodes.CALL_FUNCTION('_tmpVar3', '_tmpVar2', args=['_tmpVar4']),
		opcodes.VARIABLE(name='_tmpVar1'),
	]
	vector = execute.executed.scope['_tmpVar1']
	assert await vector.getAttribute('__class__') is execute.scope['Vector']


@pytest.mark.parametrize("length", list(range(2, 6)))
async def test_ConstVector_syntaxInit(execute, length):
	execute.executeInInitialScope('from std._std.objects.vector.vector import Vector')
	execute.executeInInitialScope('import std._std.objects.vector.vector__init')
	execute.executeInInitialScope('import std._std.objects.vector.vector__append')

	code = ', '.join(map(str, range(length)))
	execute(code)

	assert execute.parsed.code == [
		*[
			opcodes.CALL_FUNCTION_STATIC(
				f'_tmpVar{index + 1}', Number.call, staticArgs=[str(index)]
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

	assert (
		str(execute.executed.scope[f'_tmpVar{length + 1}']) == f'Vector<_head=[{code}]>'
	)


@pytest.mark.parametrize("length", list(range(2, 6)))
async def test_ConstVector_packUnpack(execute, length):
	execute.executeInInitialScope('from std._std.objects.vector.vector import Vector')
	execute.executeInInitialScope('import std._std.objects.vector.vector__init')
	execute.executeInInitialScope('import std._std.objects.vector.vector__append')
	execute.executeInInitialScope('from std._std.objects._internals import Iter')

	setCode = ', '.join(map(str, range(length)))
	getCode = ', '.join(f'v{index}' for index in range(length))
	execute(f'v = {setCode}\n{getCode} = v')

	assert execute.parsed.code == [
		*[
			opcodes.CALL_FUNCTION_STATIC(
				f'_tmpVar{index + 1}', Number.call, staticArgs=[str(index)]
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
		assert execute.executed.scope[f'v{index}'] == index
