import pytest

from actl import Parser, Buffer
from actl.syntax import SyntaxRules, Token, CustomRule, Many, IsInstance, Or


@pytest.fixture
def rules():
	return SyntaxRules()


@pytest.fixture
def parse():
	def make_parse(rules, inp):
		return list(Parser(rules, Buffer(inp)))

	return make_parse


def test_simple_replace(rules, parse):
	@rules.add(Token('a'))
	@_expect('a')
	def _(_):
		return 'r'

	assert parse(rules, ['a']) == ['r']


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

	assert parse(rules, ['a', 'b']) == ['a', 'r']


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

	assert parse(rules, ['a', 'b', 'b']) == ['a', 'r']


def test_many_with_zero_min_matches(rules, parse):
	@rules.add(Token('('), Many(Token('not_found'), min_matches=0), Token(')'))
	@_expect('(', ')')
	def _(*_):
		return 'r'

	assert parse(rules, ['a', '(', ')', 'b']) == ['a', 'r', 'b']


def test_or(rules, parse):
	or_tokens = 'b', 'c'

	@rules.add(Or(*([Token(or_token)] for or_token in or_tokens)))
	def _(token):
		assert token in or_tokens
		return 'r'

	for or_token in or_tokens:
		assert parse(rules, ['a', or_token, 'd']) == ['a', 'r', 'd']


# def test_call(rules, parse):
# 	@rules.add(
# 		IsInstance(VARIABLE),
# 		Token('('),
# 		Many(IsInstance(VARIABLE), min_matches=0),
# 		Token(')'),
# 		use_parser=True
# 	)

def _expect(*expect):
	def decorator(func):
		def wrapper(*args, **kwargs):
			assert expect == args
			return func(*args, **kwargs)
		return wrapper
	return decorator

# def test_dreplace_pattern(rules, parse):
# 	from std import RULES
# 	assert parse(RULES, "print('1')") == [1]
