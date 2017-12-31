
from ..code import Code
from ..parser import Parser
from ..code.opcodes.opcodes import RULES


class Project:
	def __init__(self, main):
		self.parser = Parser(main)
		buff = list(self.parser)
		print(buff)
		self.code = Code(buff, rules=RULES)
		buff = list(self.code)
		print(buff)
