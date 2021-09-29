ORDER_KEY = 3


async def test_String__init(execute):
	execute.executeInInitialScope('from std._std.objects.string.string import String')

	execute(
		's = String()\n'
	)

	assert str(execute.executed.scope['s']) == str(await execute.executed.scope['String'].call())


async def test_String__length(execute):
	execute.executeInInitialScope('from std._std.objects.string.string import String')
	execute.executeInInitialScope('import std._std.objects.string.string__length')

	execute(
		's = String()\n'
		'r = s.length'
	)

	assert str(execute.executed.scope['r']) == str(await execute.executed.scope['Number'].call(0))


def test_String__index(execute):
	execute.executeInInitialScope('from std._std.objects.string.string import String')
	execute.executeInInitialScope('import std._std.objects.string.string__index')

	execute(
		's = String()\n'
		'r = s.index("v", -1)'
	)

	assert str(execute.executed.scope['r']) == 'NoneType<>'


def test_String__split(execute):
	execute.executeInInitialScope('from std._std.objects.string.string import String')
	execute.executeInInitialScope('import std._std.objects.string.string__split')

	execute(
		's = String()\n'
		'r = s.split("v")'
	)

	assert str(execute.executed.scope['r']) == 'NoneType<>'
