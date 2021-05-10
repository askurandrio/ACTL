def test_varWithEndLine(execute):
	execute('stdI')

	assert str(execute.executed.scope['stdI']) == 'Number<1>'
