
from ..code import Code
from ..parser import Parser
from ..executor import SExecutor
from ..code.rules import RULES


class Project:
	def __init__(self, mainf):
		self.parser = Parser(open(mainf).read())
		buff = list(self.parser)
		self.code = Code(buff, rules=RULES)
		print(self.code)
		self.code.compile()
		print(self.code)
		self.executor = SExecutor(self.code)
		self.executor.exec()

