
import unittest

from actl import Code, Parser
from actl.code import opcodes
from actl.tokenizer import tokens
from actl.syntax import SyntaxRules, Or, Maybe, Many, Range, Value
from std.Scope import Scope


class test_SyntaxRule(unittest.TestCase):
	def init(self, code_variant=None):
		scope = Scope()
		if (code_variant == 'simple') or (code_variant == 'or'):
			buff = [tokens.VARIABLE('a'),
					  tokens.VARIABLE('b'),
					  tokens.VARIABLE('c'),
					  tokens.VARIABLE('d')]
		elif code_variant == 'maybe':
			buff = [tokens.VARIABLE('a'),
					  tokens.VARIABLE('b'),
					  tokens.VARIABLE('_'),
					  tokens.VARIABLE('b')]
		elif code_variant == 'many':
			buff = [tokens.VARIABLE('a'),
					  tokens.VARIABLE('a'),
					  tokens.VARIABLE('a'),
					  tokens.VARIABLE('b'),
					  tokens.VARIABLE('b'),
					  tokens.VARIABLE('z'),
					  tokens.VARIABLE('b')]
		elif code_variant == 'range':
			buff = [tokens.VARIABLE('_'),
					  tokens.VARIABLE('['),
					  tokens.VARIABLE('a'),
					  tokens.VARIABLE('['),
					  tokens.VARIABLE('b'),
					  tokens.VARIABLE(']'),
					  tokens.VARIABLE('c'),
					  tokens.VARIABLE(']'),
					  tokens.VARIABLE('_')]
		elif code_variant == 'Value':
			scope[tokens.VARIABLE('a')] = 1
			buff = [tokens.VARIABLE('b'),
					  tokens.VARIABLE('a'),
					  tokens.VARIABLE('b')]
		elif code_variant == 'ToSpecific':
			buff = [tokens.VARIABLE('_'),
					  tokens.VARIABLE('['),
					  tokens.VARIABLE('a'),
					  tokens.VARIABLE('['),
					  tokens.VARIABLE('b'),
					  tokens.VARIABLE(']'),
					  tokens.VARIABLE('b')]

		return Parser(buff, scope, SyntaxRules())

	def test_simple(self):
		parser = self.init('simple')

		@parser.rules.add(tokens.VARIABLE('b'), tokens.VARIABLE('c'))
		def _(buff):
			yield tokens.VARIABLE(buff.pop(0).name + buff.pop(0).name)

		code = list(parser.parse())
		self.assertEqual(code, [tokens.VARIABLE('a'),
										tokens.VARIABLE('bc'),
										tokens.VARIABLE('d')])

	def test_or(self):
		parser = self.init('or')

		@parser.rules.add(Or((tokens.VARIABLE('b'),), (tokens.VARIABLE('d'),)))
		def _(buff):
			yield tokens.VARIABLE(f'Or({buff.pop(0).name})')

		code = list(parser.parse())
		self.assertEqual(code, [tokens.VARIABLE('a'),
										tokens.VARIABLE('Or(b)'),
										tokens.VARIABLE('c'),
										tokens.VARIABLE('Or(d)')])

	def test_maybe(self):
		parser = self.init('maybe')

		@parser.rules.add(tokens.VARIABLE('b'))
		def _(buff):
			yield tokens.VARIABLE(f'Single({buff.pop(0).name})')

		@parser.rules.add(Maybe(tokens.VARIABLE('a')), tokens.VARIABLE('b'))
		def _(buff):
			yield tokens.VARIABLE(f'Maybe({buff.pop(0).name}, {buff.pop(0).name})')

		code = list(parser.parse())
		self.assertEqual(code, [tokens.VARIABLE('Maybe(a, b)'),
										tokens.VARIABLE('_'),
										tokens.VARIABLE('Single(b)')])

	def test_many(self):
		parser = self.init('many')

		@parser.rules.add(Many(tokens.VARIABLE('a'), minimum=3))
		def _(buff):
			name = ''
			while tokens.VARIABLE('a') == buff.get(0):
				name += buff.pop(0).name
			yield tokens.VARIABLE(f'Many({name})')

		@parser.rules.add(Many(tokens.VARIABLE('b'), minimum=2))
		def _(buff):
			name = ''
			while tokens.VARIABLE('b') == buff.get(0):
				name += buff.pop(0).name
			yield tokens.VARIABLE(f'Many({name})')

		code = list(parser.parse())
		self.assertEqual(code, [tokens.VARIABLE('Many(aaa)'),
										tokens.VARIABLE('Many(bb)'),
										tokens.VARIABLE('z'),
										tokens.VARIABLE('b')])

	def test_range(self):
		parser = self.init('range')

		@parser.rules.add(Range((tokens.VARIABLE('['),), lambda _: (tokens.VARIABLE(']'),)))
		def _(buff):
			name = ''
			name += buff.pop(0).name
			count = 1
			while count:
				elem = buff.pop(0)
				if tokens.VARIABLE('[') == elem:
					count += 1
				elif tokens.VARIABLE(']') == elem:
					count -= 1
				name += elem.name
			yield tokens.VARIABLE(f'Range({name})')

		code = list(parser.parse())
		self.assertEqual(code, [tokens.VARIABLE('_'),
										tokens.VARIABLE('Range([a[b]c])'),
										tokens.VARIABLE('_')])

	def test_value(self):
		parser = self.init('Value')

		@parser.rules.add(Value(1), args=('scope', 'buff'))
		def _(scope, buff):
			value = parser.scope[buff.pop(0)]
			yield tokens.VARIABLE(f'Value({value})')

		code = list(parser.parse())
		self.assertEqual(code, [tokens.VARIABLE('b'),
										tokens.VARIABLE('Value(1)'),
										tokens.VARIABLE('b')])
