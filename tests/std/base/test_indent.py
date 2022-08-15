import pytest


ORDER_KEY = 9


async def test_spacesBeforeCodeIsForbidden(execute):
	execute(' a = 1')

	with pytest.raises(RuntimeError) as ex:
		execute.parsed.code.loadAll()

	assert (
		str(ex.value)
		== "Error during parsing at buff<Buffer([' ', 'a', ' ', '=', ' ', '1'])>"
	)
