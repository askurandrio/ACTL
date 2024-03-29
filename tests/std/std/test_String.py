ORDER_KEY = 4


async def test_String__init(execute):
	execute('s = String()\n')

	assert str(execute.executed.scope['s']) == ''


async def test_String_syntaxInit(execute):
	execute('s = ""\n')

	assert str(execute.executed.scope['s']) == ''


async def test_String__length(execute):
	execute('s = String()\nr = s.length')

	assert str(execute.executed.scope['r']) == 'Number<_head=PyToA<0>>'


async def test_String_lengthFromSyntaxInit(execute):
	execute('s = ""\nr = s.length')

	assert str(execute.executed.scope['r']) == 'Number<_head=PyToA<0>>'


async def test_String__split(execute):
	execute("s = '1v2'\nr = s.split('v')")

	assert str(execute.executed.scope['r']) == "Vector<_head=PyToA<[1, 2]>>"
