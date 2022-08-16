# pylint: disable=line-too-long

import pytest


ORDER_KEY = 9


async def test_spacesBeforeCodeIsForbidden(execute):
	execute(' a = 1')

	with pytest.raises(RuntimeError) as ex:
		execute.parsed.code.loadAll()

	assert (
		repr(ex.value)
		== 'RuntimeError("Error during parsing at buff<Buffer([\' \', \'a\', \' \', \'=\', \' \', \'1\'])>Speces before code is forbidden: Buffer([\' \', \'a\', \' \', \'=\', \' \', \'1\'])")'
	)


async def test_spacesBeforeCodeIsForbiddenCheckedOnFirstInstruction(execute):
	execute('while True:\n	 a = 1\n b = 2')

	with pytest.raises(RuntimeError) as ex:
		assert execute.executed.scope

	assert (
		str(ex.value)
		== "Error during parsing at buff<Buffer([' ', 'b'])>Speces before code after block is forbidden: Buffer([' ', 'b'])"
	)
