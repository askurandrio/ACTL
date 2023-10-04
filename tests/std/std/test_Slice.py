from unittest.mock import Mock

from actl import opcodes
from actl.objects import Object, PyToA, AToPy


ORDER_KEY = 3


async def test_Slice__init(execute):
	execute('s = Slice(1, 2, 3)\n')

	assert (
		str(execute.executed.scope['s'])
		== 'Slice<start=Number<_head=PyToA<1>>, stop=Number<_head=PyToA<2>>, step=Number<_head=PyToA<3>>>'
	)


async def test_Slice_syntaxInit(execute):
	collection = await Object.call()
	getItemMock = Mock()
	await collection.setAttribute('__getItem__', await PyToA.call(getItemMock))
	execute.scope['collection'] = collection

	execute('collection[2:]')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			'#1', 'Number', staticArgs=[await PyToA.call('2')]
		),
		opcodes.CALL_FUNCTION_STATIC('#2', 'Slice', args=['#1', 'None', 'None']),
		opcodes.GET_ATTRIBUTE('#3', 'collection', '__getItem__'),
		opcodes.CALL_FUNCTION('#4', '#3', args=['#2']),
		opcodes.VARIABLE('#4'),
	]

	assert await AToPy(execute.executed.scope['#4']) == getItemMock.return_value
	getItemMock.assert_called_once_with(await AToPy(execute.executed.scope['#2']))
	assert (
		str(execute.executed.scope['#2'])
		== 'Slice<start=Number<_head=PyToA<2>>, stop=NoneType<>, step=↑...>'
	)
