ORDER_KEY = 2


def test_String__split(execute):
	execute(
		's = String()\n'
		'r = s.split("v")'
	)

	assert str(execute.executed.scope['r']) == 'NoneType<>'
