async def test_Slice__init(execute):
	execute.executeInInitialScope('from std._std.objects.slice import Slice')

	execute(
		's = Slice(1, 2, 3)\n'
	)

	assert str(execute.executed.scope['s']) == 'Slice<start=Number<1>, stop=Number<2>, step=Number<3>>'
