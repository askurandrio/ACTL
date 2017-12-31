
from ..code import Code
from ..parser import Parser
from ..code.opcodes.opcodes import RULES


class Project:
	def __init__(self, mainf):
		self.parser = Parser(open(mainf).read())
		buff = list(self.parser)
		print(buff)
		self.code = Code(buff, rules=RULES)
		self.code.compile()
		buff = list(self.code)
		print(buff)
