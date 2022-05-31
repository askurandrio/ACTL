ORDER_KEY = 3


async def test_String__init(execute):
	execute.executeInInitialScope('from std._std.objects.string.string import String')

	execute('s = String()\n')

	assert str(execute.executed.scope['s']) == ''


async def test_String_syntaxInit(execute):
	execute.executeInInitialScope('from std._std.objects.string.string import String')

	execute('s = ""\n')

	assert str(execute.executed.scope['s']) == ''


async def test_String__length(execute):
	execute.executeInInitialScope('from std._std.objects.string.string import String')
	execute.executeInInitialScope('import std._std.objects.string.string__length')

	execute('s = String()\n' 'r = s.length')

	assert execute.executed.scope['r'] == await execute.executed.scope['Number'].call(0)


async def test_String_lengthFromSyntaxInit(execute):
	execute.executeInInitialScope('from std._std.objects.string.string import String')
	execute.executeInInitialScope('import std._std.objects.string.string__length')

	execute('s = ""\n' 'r = s.length')

	assert execute.executed.scope['r'] == await execute.executed.scope['Number'].call(0)


async def test_String__split(execute):
	execute.executeInInitialScope('from std._std.objects.string.string import String')
	execute.executeInInitialScope('import std._std.objects.string.string__split')

	execute("s = '1v2'\nr = s.split('v')")

	assert str(execute.executed.scope['r']) == "Vector<_head=['1', '2']>"
