ORDER_KEY = 1


def test_Vector__append(execute):
	execute.executeInInitialScope('from std._std.objects.vector import Vector')

	execute(
		'v = Vector()\n'
		'v.append(1)'
	)

	assert str(execute.executed.scope['v']) == 'Vector<_head=[1]>'
