import pytest

from actl import Parser, Buffer, opcodes
from std import RULES


@pytest.fixture
def parse():
	def parse_(rules, inp):
		opcodes.VARIABLE.counter.reset()
		return list(Parser(rules, Buffer(inp)))

	return parse_


def test_call(parse):
	assert parse(RULES, "print()") == [
		opcodes.CALL_FUNCTION(dst='__IV11', function='print', typeb='(', args=[], kwargs={}),
		opcodes.VARIABLE(name='__IV11')
	]


def test_call_with_empty_string(parse):
	assert parse(RULES, "print('')") == [
		opcodes.BUILD_STRING(dst=opcodes.VARIABLE(name='__IV11'), string=''),
		opcodes.CALL_FUNCTION(dst='__IV12', function='print', typeb='(', args=['__IV11'], kwargs={}),
		opcodes.VARIABLE(name='__IV12')
	]


def test_call_with_string(parse):
	assert parse(RULES, "print('s')") == [
		opcodes.BUILD_STRING(dst=opcodes.VARIABLE(name='__IV11'), string='s'),
		opcodes.CALL_FUNCTION(dst='__IV12', function='print', typeb='(', args=['__IV11'], kwargs={}),
		opcodes.VARIABLE(name='__IV12')
	]
