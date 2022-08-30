# pylint: disable=line-too-long

import pytest

from actl import Buffer


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


async def test_lineWithOnlySpacesAllowed(execute):
	execute('  \n')

	assert execute.executed.scope


@pytest.mark.parametrize("code", [' \t\n', '\t \n'])
def test_mixedIndentationIsForbidden(execute, code):
	codeRepr = Buffer(code).loadAll()
	execute(code)

	with pytest.raises(RuntimeError) as ex:
		assert execute.executed.scope

	assert (
		str(ex.value)
		== f"Error during parsing at buff<{codeRepr}>Mixed indentation is forbidden: {codeRepr}"
	)
