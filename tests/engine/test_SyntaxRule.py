
import unittest

from actl import Code
from actl.parser import opcodes
from actl.code.SyntaxRule import SyntaxRules


class test_SyntaxRule(unittest.TestCase):
	def init(self):
		rules = SyntaxRules()
		code = Code(None, rules, None)
		return code, rules

	def test_simple(self):
		code, rules = self.init()
		code.buff = [opcodes.VARIABLE('a'),
						 opcodes.VARIABLE('b'),
						 opcodes.VARIABLE('c'),
						 opcodes.VARIABLE('d')]

		@rules.add(opcodes.VARIABLE('b'), opcodes.VARIABLE('c'))
		def _(code, var1, var2, *args):
			return (opcodes.VARIABLE(var1.name + var2.name),)

		code.compile()
		self.assertEqual(code.buff, [opcodes.VARIABLE('a'),
											  opcodes.VARIABLE('bc'),
											  opcodes.VARIABLE('d')])
