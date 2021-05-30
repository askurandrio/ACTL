ORDER_KEY = 1


def test_VectorAppend(execute):
	execute(
		'v = Vector()\n'
		'v.append(1)'
	)

	assert str(execute.executed.scope['v']) == 'Vector<_head=[1]>'
