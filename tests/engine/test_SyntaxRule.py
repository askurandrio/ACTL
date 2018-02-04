
import unittest

from actl import Code
from actl.code.opcodes import opcodes
from actl.syntax import SyntaxRules, Or, Maybe, Many, Range, Value


class test_SyntaxRule(unittest.TestCase):
	def init(self, code_variant=None):
		rules = SyntaxRules()
		code = Code(None, rules, None)
		if (code_variant == 'simple') or (code_variant == 'or'):
			code.buff = [opcodes.VARIABLE('a'),
							 opcodes.VARIABLE('b'),
							 opcodes.VARIABLE('c'),
							 opcodes.VARIABLE('d')]
		elif code_variant == 'maybe':
			code.buff = [opcodes.VARIABLE('a'),
							 opcodes.VARIABLE('b'),
							 opcodes.VARIABLE('_'),
							 opcodes.VARIABLE('b')]
		elif code_variant == 'many':
			code.buff = [opcodes.VARIABLE('a'),
							 opcodes.VARIABLE('a'),
							 opcodes.VARIABLE('a'),
							 opcodes.VARIABLE('b'),
							 opcodes.VARIABLE('b'),
							 opcodes.VARIABLE('z'),
							 opcodes.VARIABLE('b')]
		elif code_variant == 'range':
			code.buff = [opcodes.VARIABLE('_'),
							 opcodes.VARIABLE('['),
							 opcodes.VARIABLE('a'),
							 opcodes.VARIABLE('['),
							 opcodes.VARIABLE('b'),
							 opcodes.VARIABLE(']'),
							 opcodes.VARIABLE('c'),
							 opcodes.VARIABLE(']'),
							 opcodes.VARIABLE('_')]

		return code, rules

	def test_simple(self):
		code, rules = self.init('simple')

		@rules.add(opcodes.VARIABLE('b'), opcodes.VARIABLE('c'))
		def _(var1, var2):
			return (opcodes.VARIABLE(var1.name + var2.name),)

		code.compile()
		self.assertEqual(code.buff, [opcodes.VARIABLE('a'),
											  opcodes.VARIABLE('bc'),
											  opcodes.VARIABLE('d')])

	def test_or(self):
		code, rules = self.init('or')

		@rules.add(Or((opcodes.VARIABLE('b'),), (opcodes.VARIABLE('d'),)))
		def _(var):
			return (opcodes.VARIABLE(f'Or({var.name})'),)

		code.compile()
		self.assertEqual(code.buff, [opcodes.VARIABLE('a'),
											  opcodes.VARIABLE('Or(b)'),
											  opcodes.VARIABLE('c'),
											  opcodes.VARIABLE('Or(d)')])

	def test_maybe(self):
		code, rules = self.init('maybe')

		@rules.add(opcodes.VARIABLE('b'))
		@rules.add(Maybe(opcodes.VARIABLE('a')), opcodes.VARIABLE('b'))
		def _(var1, var2=None):
			if var2 is None:
				opcode = opcodes.VARIABLE(f'Single({var1.name})')
			else:
				opcode = opcodes.VARIABLE(f'Maybe({var1.name}, {var2.name})')
			return (opcode,)

		code.compile()
		self.assertEqual(code.buff, [opcodes.VARIABLE('Maybe(a, b)'),
											  opcodes.VARIABLE('_'),
											  opcodes.VARIABLE('Single(b)')])

	def test_many(self):
		code, rules = self.init('many')

		@rules.add(Many(opcodes.VARIABLE('a'), minimum=3))
		@rules.add(Many(opcodes.VARIABLE('b'), minimum=2))
		def _(*matched_code):
			name = ''.join(var.name for var in matched_code)
			return (opcodes.VARIABLE(f'Many({name})'),)

		code.compile()
		self.assertEqual(code.buff, [opcodes.VARIABLE('Many(aaa)'),
											  opcodes.VARIABLE('Many(bb)'),
											  opcodes.VARIABLE('z'),
											  opcodes.VARIABLE('b')])

	def test_range(self):
		code, rules = self.init('range')

		@rules.add(Range((opcodes.VARIABLE('['),), lambda _: (opcodes.VARIABLE(']'),)))
		def _(*matched_code):
			name = ''.join(var.name for var in matched_code)
			return (opcodes.VARIABLE(f'Range({name})'),)

		code.compile()
		self.assertEqual(code.buff, [opcodes.VARIABLE('_'),
											  opcodes.VARIABLE('Range([a[b]c])'),
											  opcodes.VARIABLE('_')])

	def test_range(self):
		code, rules = self.init('range')

		@rules.add(Range((opcodes.VARIABLE('['),), lambda _: (opcodes.VARIABLE(']'),)))
		def _(*matched_code):
			name = ''.join(var.name for var in matched_code)
			return (opcodes.VARIABLE(f'Range({name})'),)

		code.compile()
		self.assertEqual(code.buff, [opcodes.VARIABLE('_'),
											  opcodes.VARIABLE('Range([a[b]c])'),
											  opcodes.VARIABLE('_')])

