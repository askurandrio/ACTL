from unittest.mock import Mock

from actl import opcodes
from actl.objects import Object, PyToA, Number, AToPy


ORDER_KEY = 2


async def test_Slice__init(execute):
	execute.executeInInitialScope('from std._std.objects.slice import Slice')

	execute(
		's = Slice(1, 2, 3)\n'
	)

	assert str(execute.executed.scope['s']) == 'Slice<start=Number<1>, stop=Number<2>, step=Number<3>>'

async def test_Slice_syntaxInit(execute):
	execute.executeInInitialScope('from std._std.objects.slice import Slice')
	collection = await Object.call()
	getItemMock = Mock()
	collection.setAttribute('__getItem__', await PyToA.call(getItemMock))
	execute.scope['collection'] = collection

	execute('collection[2:]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', Number.call, staticArgs=['2']),
		opcodes.CALL_FUNCTION_STATIC('_tmpVar2', 'Slice', args=['_tmpVar1', 'None', 'None']),
		opcodes.GET_ATTRIBUTE('_tmpVar3', 'collection', '__getItem__'),
		opcodes.CALL_FUNCTION('_tmpVar4', '_tmpVar3', args=['_tmpVar2']),
		opcodes.VARIABLE('_tmpVar4')
	]

	assert AToPy(execute.executed.scope['_tmpVar4']) == getItemMock.return_value
	getItemMock.assert_called_once_with(AToPy(execute.executed.scope['_tmpVar2']))
	assert str(execute.executed.scope['_tmpVar2']) == 'Slice<start=Number<2>, stop=NoneType<>, step=↑...>'
