import pytest

from actl import Parser, Buffer, opcodes, Scope
from std import RULES


@pytest.fixture
def parse():
	def _parse(inp):
		opcodes.VARIABLE.counter.reset()
		scope = Scope({})
		inp = Buffer(inp)
		return list(Parser(scope, RULES, inp))

	return _parse


def test_call(parse):
	assert parse("print()") == [
		opcodes.CALL_FUNCTION(dst='__IV11', function='print', typeb='(', args=[], kwargs={}),
		opcodes.VARIABLE(name='__IV11')
	]


def test_call_with_empty_string(parse):
	assert parse("print('')") == [
		opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function='String', args=['']),
		opcodes.CALL_FUNCTION(dst='__IV12', function='print', typeb='(', args=['__IV11'], kwargs={}),
		opcodes.VARIABLE(name='__IV12')
	]


def test_call_with_string(parse):
	assert parse("print('s')") == [
		opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function='String', args=['s']),
		opcodes.CALL_FUNCTION(dst='__IV12', function='print', typeb='(', args=['__IV11'], kwargs={}),
		opcodes.VARIABLE(name='__IV12')
	]
