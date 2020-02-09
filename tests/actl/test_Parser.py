# pylint: disable=redefined-outer-name

import pytest

from actl import Parser, Buffer, Scope
from actl.opcodes import VARIABLE
from actl.syntax import SyntaxRules, Token, Many, IsInstance, Or, Maybe, Value, \
	SyntaxRule, CustomTemplate


@pytest.fixture
def parse():
	def _parse(scope, rules, inp):
		scope = Scope(scope)
		rules = SyntaxRules(rules)
		inp = Buffer(inp)
		parser = Parser(scope, rules, inp)
		return list(parser)

	return _parse


def test_simple_replace(parse):
	@SyntaxRule.wrap(Token('b'))
	@_expect('b')
	def rule(_):
		return 'r'

	assert parse({}, [rule], ['a', 'b', 'c']) == ['a', 'r', 'c']


def test_replace_pattern(parse):
	@SyntaxRule.wrap(Token('b'), Token('c'))
	@_expect('b', 'c')
	def rule(*_):
		return 'r'

	assert parse({}, [rule], ['a', 'b', 'c', 'd']) == ['a', 'r', 'd']


def test_custom_template(parse):
	@SyntaxRule.wrap(CustomTemplate.createToken(lambda _, token: token == 'b', 'token'))
	@_expect('b')
	def rule(_):
		return 'r'

	assert parse({}, [rule], ['a', 'b', 'c']) == ['a', 'r', 'c']


def test_isinstance(parse):
	@SyntaxRule.wrap(IsInstance(int))
	@_expect(1)
	def rule(_):
		return 'r'

	assert parse({}, [rule], [1]) == ['r']


def test_many(parse):
	@SyntaxRule.wrap(Many(Token('b')))
	@_expect('b', 'b')
	def rule(*_):
		return 'r'

	assert parse({}, [rule], ['a', 'b', 'b', 'c']) == ['a', 'r', 'c']


def test_or(parse):
	or_tokens = 'b', 'c'

	@SyntaxRule.wrap(Or(*([Token(or_token)] for or_token in or_tokens)))
	def rule(token):
		assert token in or_tokens
		return 'r'

	for or_token in or_tokens:
		assert parse({}, [rule], ['a', or_token, 'd']) == ['a', 'r', 'd']


def test_maybe(parse):
	@SyntaxRule.wrap(Or([Token('b')], [Token('c')]), Maybe(Token('d')))
	def rule(first_token, second_token=None):
		if first_token == 'b':
			assert second_token is None
		elif first_token == 'c':
			assert second_token == 'd'
		else:
			assert False, second_token
		return 'r'

	assert parse({}, [rule], ['a', 'b', 'e']) == ['a', 'r', 'e']
	assert parse({}, [rule], ['a', 'c', 'd', 'e']) == ['a', 'r', 'e']


def test_replace_after_replace(parse):
	@SyntaxRule.wrap(Token('b'))
	@_expect('b')
	def first_rule(_):
		return ['d']

	@SyntaxRule.wrap(Token('d'))
	@_expect('d')
	def second_rule(_):
		return 'r'

	assert parse({}, [first_rule, second_rule], ['a', 'b', 'c']) == ['a', 'r', 'c']


def test_value(parse):
	@SyntaxRule.wrap(Token('a'))
	@_expect('a')
	def token_to_variable(_):
		return [VARIABLE('a')]

	@SyntaxRule.wrap(Value(1))
	@_expect(VARIABLE('a'))
	def variable_to_value(_):
		return 'b'

	assert parse({'a': 1}, [token_to_variable, variable_to_value], ['a']) == ['b']


def _expect(*expect):
	def decorator(func):
		def wrapper(*args, **kwargs):
			assert expect == args, func
			return func(*args, **kwargs)

		return wrapper

	return decorator
