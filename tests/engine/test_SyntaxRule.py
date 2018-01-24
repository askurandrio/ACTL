
import unittest

from actl import Code
from actl.parser import opcodes
from actl.syntax.SyntaxRule import Or, Not, SyntaxRules


class test_SyntaxRule(unittest.TestCase):
	def init(self, code_variant=None):
		rules = SyntaxRules()
		code = Code(None, rules, None)
		if (code_variant == 'simple') or (code_variant == 'or'):
			code.buff = [opcodes.VARIABLE('a'),
							 opcodes.VARIABLE('b'),
							 opcodes.VARIABLE('c'),
							 opcodes.VARIABLE('d')]
		elif code_variant == 'not':
			code.buff = [opcodes.VARIABLE('a'),
							 opcodes.VARIABLE('b'),
							 opcodes.VARIABLE('c'),
							 opcodes.VARIABLE('b')]
		return code, rules

	def test_simple(self):
		code, rules = self.init('simple')

		@rules.add(opcodes.VARIABLE('b'), opcodes.VARIABLE('c'))
		def _(_, var1, var2):
			return (opcodes.VARIABLE(var1.name + var2.name),)

		code.compile()
		self.assertEqual(code.buff, [opcodes.VARIABLE('a'),
											  opcodes.VARIABLE('bc'),
											  opcodes.VARIABLE('d')])

	def test_or(self):
		code, rules = self.init('or')

		@rules.add(Or((opcodes.VARIABLE('b'),), (opcodes.VARIABLE('c'),)))
		def _(_, var1, var2):
			return (opcodes.VARIABLE(f'Or({var1.name}, {var2.name})'),)

		code.compile()
		self.assertEqual(code.buff, [opcodes.VARIABLE('a'),
											  opcodes.VARIABLE('Or(b, c)'),
											  opcodes.VARIABLE('d')])

	def test_not(self):
		code, rules = self.init('not')

		@rules.add(Not((opcodes.VARIABLE('a'),), (opcodes.VARIABLE('c'),)))
		def _(_, var1, var2):
			return (opcodes.VARIABLE(f'Not({var1.name}, {var2.name})'),)

		code.compile()
		self.assertEqual(code.buff, [opcodes.VARIABLE('a'),
											  opcodes.VARIABLE('b'),
											  opcodes.VARIABLE('Not(c, b)'),])
