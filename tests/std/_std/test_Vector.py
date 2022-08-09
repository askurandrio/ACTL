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


async def test_Const_Vector_syntaxInit(execute):
	execute.executeInInitialScope('from std._std.objects.vector.vector import Vector')
	execute.executeInInitialScope('import std._std.objects.vector.vector__init')
	execute.executeInInitialScope('import std._std.objects.vector.vector__append')

	execute('1, 2, 3')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', Number.call, staticArgs=['1']),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar2', Number.call, staticArgs=['2']),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar3', Number.call, staticArgs=['3']),
		opcodes.CALL_FUNCTION_STATIC(
			'_tmpVar4', vector__of.call, args=['_tmpVar1', '_tmpVar2', '_tmpVar3']
		),
		opcodes.VARIABLE('_tmpVar4'),
	]

	assert str(execute.executed.scope['_tmpVar4']) == 'Vector<_head=[1, 2, 3]>'
