import pytest

from actl import Parser, Buffer
from actl.syntax import SyntaxRules, Token, CustomRule, Many, IsInstance, Or, Maybe


@pytest.fixture
def rules():
	return SyntaxRules()


@pytest.fixture
def parse():
	def make_parse(rules, inp):
		return list(Parser(rules, Buffer(inp)))

	return make_parse


def test_simple_replace(rules, parse):
	@rules.add(Token('b'))
	@_expect('b')
	def _(_):
		return 'r'

	assert parse(rules, ['a', 'b', 'c']) == ['a', 'r', 'c']


def test_replace_pattern(rules, parse):
	@rules.add(Token('b'), Token('c'))
	@_expect('b', 'c')
	def _(*_):
		return 'r'

	assert parse(rules, ['a', 'b', 'c', 'd']) == ['a', 'r', 'd']


def test_custom_func(rules, parse):
	@rules.add(CustomRule('test', lambda token: token == 'b'))
	@_expect('b')
	def _(_):
		return 'r'

	assert parse(rules, ['a', 'b', 'c']) == ['a', 'r', 'c']


def test_isinstance(rules, parse):
	@rules.add(IsInstance(int))
	@_expect(1)
	def _(_):
		return 'r'

	assert parse(rules, [1]) == ['r']


def test_many(rules, parse):
	@rules.add(Many(Token('b')))
	@_expect('b', 'b')
	def _(*_):
		return 'r'

	assert parse(rules, ['a', 'b', 'b', 'c']) == ['a', 'r', 'c']


def test_or(rules, parse):
	or_tokens = 'b', 'c'

	@rules.add(Or(*([Token(or_token)] for or_token in or_tokens)))
	def _(token):
		assert token in or_tokens
		return 'r'

	for or_token in or_tokens:
		assert parse(rules, ['a', or_token, 'd']) == ['a', 'r', 'd']


def test_maybe(rules, parse):
	@rules.add(Or([Token('b')], [Token('c')]), Maybe(Token('d')))
	def _(first_token, second_token=None):
		if first_token == 'b':
			assert second_token is None
		elif first_token == 'c':
			assert second_token == 'd'
		else:
			assert False, second_token
		return 'r'

	assert parse(rules, ['a', 'b', 'e']) == ['a', 'r', 'e']
	assert parse(rules, ['a', 'c', 'd', 'e']) == ['a', 'r', 'e']


def test_replace_after_replace(rules, parse):
	@rules.add(Token('b'))
	@_expect('b')
	def _(_):
		return 'd'

	@rules.add(Token('d'))
	@_expect('d')
	def _(_):
		return 'r'

	assert parse(rules, ['a', 'b', 'c']) == ['a', 'r', 'c']


def test_call(parse):
	from std import RULES

	assert parse(RULES, "print('')") == []


def _expect(*expect):
	def decorator(func):
		def wrapper(*args, **kwargs):
			assert expect == args
			return func(*args, **kwargs)
		return wrapper
	return decorator
