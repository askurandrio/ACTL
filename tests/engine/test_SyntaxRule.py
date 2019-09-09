import pytest

from actl import Parser, Buffer
from actl.syntax import SyntaxRules, Token


@pytest.fixture
def rules():
	return SyntaxRules()


@pytest.fixture
def parse():
	def make_parse(rules, inp):
		parser = Parser(rules, Buffer(inp))
		return list(parser)
	return make_parse


def test_simple(rules, parse):
	@rules.add(Token('a'))
	def _(_):
		return 'b'

	assert parse(rules, ['a']) == ['b']
