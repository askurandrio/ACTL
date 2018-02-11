
import unittest

from actl import Code
from actl.code import opcodes
from actl.parser import tokens
from actl.syntax import SyntaxRules, Or, Maybe, Many, Range, Value, ToSpecific
from pyport import Scope


class test_SyntaxRule(unittest.TestCase):
	def init(self, code_variant=None):
		rules = SyntaxRules()
		code = Code(None, rules, None)
		if (code_variant == 'simple') or (code_variant == 'or'):
			code.buff = [tokens.VARIABLE('a'),
							 tokens.VARIABLE('b'),
							 tokens.VARIABLE('c'),
							 tokens.VARIABLE('d')]
		elif code_variant == 'maybe':
			code.buff = [tokens.VARIABLE('a'),
							 tokens.VARIABLE('b'),
							 tokens.VARIABLE('_'),
							 tokens.VARIABLE('b')]
		elif code_variant == 'many':
			code.buff = [tokens.VARIABLE('a'),
							 tokens.VARIABLE('a'),
							 tokens.VARIABLE('a'),
							 tokens.VARIABLE('b'),
							 tokens.VARIABLE('b'),
							 tokens.VARIABLE('z'),
							 tokens.VARIABLE('b')]
		elif code_variant == 'range':
			code.buff = [tokens.VARIABLE('_'),
							 tokens.VARIABLE('['),
							 tokens.VARIABLE('a'),
							 tokens.VARIABLE('['),
							 tokens.VARIABLE('b'),
							 tokens.VARIABLE(']'),
							 tokens.VARIABLE('c'),
							 tokens.VARIABLE(']'),
							 tokens.VARIABLE('_')]
		elif code_variant == 'Value':
			code.scope = Scope()
			code.scope[tokens.VARIABLE('a')] = 1
			code.buff = [tokens.VARIABLE('b'),
							 tokens.VARIABLE('a'),
							 tokens.VARIABLE('b')]
		elif code_variant == 'ToSpecific':
			code.buff = [tokens.VARIABLE('_'),
							 tokens.VARIABLE('['),
							 tokens.VARIABLE('a'),
							 tokens.VARIABLE('['),
							 tokens.VARIABLE('b'),
							 tokens.VARIABLE(']'),
							 tokens.VARIABLE('b')]

		return code, rules

	def test_simple(self):
		code, rules = self.init('simple')

		@rules.add(tokens.VARIABLE('b'), tokens.VARIABLE('c'))
		def _(var1, var2):
			return (tokens.VARIABLE(var1.name + var2.name),)

		code.compile()
		self.assertEqual(code.buff, [tokens.VARIABLE('a'),
											  tokens.VARIABLE('bc'),
											  tokens.VARIABLE('d')])

	def test_or(self):
		code, rules = self.init('or')

		@rules.add(Or((tokens.VARIABLE('b'),), (tokens.VARIABLE('d'),)))
		def _(var):
			return (tokens.VARIABLE(f'Or({var.name})'),)

		code.compile()
		self.assertEqual(code.buff, [tokens.VARIABLE('a'),
											  tokens.VARIABLE('Or(b)'),
											  tokens.VARIABLE('c'),
											  tokens.VARIABLE('Or(d)')])

	def test_maybe(self):
		code, rules = self.init('maybe')

		@rules.add(tokens.VARIABLE('b'))
		@rules.add(Maybe(tokens.VARIABLE('a')), tokens.VARIABLE('b'))
		def _(var1, var2=None):
			if var2 is None:
				opcode = tokens.VARIABLE(f'Single({var1.name})')
			else:
				opcode = tokens.VARIABLE(f'Maybe({var1.name}, {var2.name})')
			return (opcode,)

		code.compile()
		self.assertEqual(code.buff, [tokens.VARIABLE('Maybe(a, b)'),
											  tokens.VARIABLE('_'),
											  tokens.VARIABLE('Single(b)')])

	def test_many(self):
		code, rules = self.init('many')

		@rules.add(Many(tokens.VARIABLE('a'), minimum=3))
		@rules.add(Many(tokens.VARIABLE('b'), minimum=2))
		def _(*matched_code):
			name = ''.join(var.name for var in matched_code)
			return (tokens.VARIABLE(f'Many({name})'),)

		code.compile()
		self.assertEqual(code.buff, [tokens.VARIABLE('Many(aaa)'),
											  tokens.VARIABLE('Many(bb)'),
											  tokens.VARIABLE('z'),
											  tokens.VARIABLE('b')])

	def test_range(self):
		code, rules = self.init('range')

		@rules.add(Range((tokens.VARIABLE('['),), lambda _: (tokens.VARIABLE(']'),)))
		def _(*matched_code):
			name = ''.join(var.name for var in matched_code)
			return (tokens.VARIABLE(f'Range({name})'),)

		code.compile()
		self.assertEqual(code.buff, [tokens.VARIABLE('_'),
											  tokens.VARIABLE('Range([a[b]c])'),
											  tokens.VARIABLE('_')])

	def test_range(self):
		code, rules = self.init('range')

		@rules.add(Range((tokens.VARIABLE('['),), lambda _: (tokens.VARIABLE(']'),)))
		def _(*matched_code):
			name = ''.join(var.name for var in matched_code)
			return (tokens.VARIABLE(f'Range({name})'),)

		code.compile()
		self.assertEqual(code.buff, [tokens.VARIABLE('_'),
											  tokens.VARIABLE('Range([a[b]c])'),
											  tokens.VARIABLE('_')])

	def test_value(self):
		code, rules = self.init('Value')

		@rules.add(Value(1), args=('code', 'matched_code'))
		def _(code, matched_code):
			value = code.scope[matched_code[0]]
			return (tokens.VARIABLE(f'Value({value})'),)

		code.compile()
		self.assertEqual(code.buff, [tokens.VARIABLE('b'),
											  tokens.VARIABLE('Value(1)'),
											  tokens.VARIABLE('b')])

	def test_tospecific(self):
		code, rules = self.init('ToSpecific')

		@rules.add(ToSpecific(tokens.VARIABLE(']')))
		def _(*matched_code):
			name = ''.join(var.name for var in matched_code)
			return (tokens.VARIABLE(f'ToSpecific({name})'),)

		code.compile()
		self.assertEqual(code.buff, [tokens.VARIABLE('ToSpecific(_[a[b])'),
											  tokens.VARIABLE('b')])

