import sys
import pytest

from actl import opcodes
from actl.objects import String, AToPy


ORDER_KEY = 11


async def test_setString(execute):
	execute("res = 's'")

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC('_tmpVar1', String.call, staticArgs=['s']),
		opcodes.SET_VARIABLE('res', '_tmpVar1')
	]
	assert execute.executed.scope['res'] == await String.call('s')


@pytest.mark.parametrize(
	"code",
	[
		'1 + 1',
		'1 - 1',
		'1 * 1',
		'1 / 1',
		'1 < 1',
		'1 > 1',
		'1 <= 1',
		'1 >= 1',
		'1 != 1',
		'1 == 1',
	]
)
def test_equality_with_py(execute, code):
	pyResult = eval(code)  # pylint: disable=eval-used

	execute(f'result = {code}')

	try:
		aResult = AToPy(execute.executed.scope['result'])
	except:
		print('Code parsed as', execute.parsed.code, file=sys.stderr)
		raise

	assert pyResult == aResult
