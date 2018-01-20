
from ..code import Code
from ..parser import Parser
from ..executor import SExecutor
from ..code.rules import RULES


class Project:
	__this = None

	def __init__(self, mainf):
		self.__class__.__this = self
		code = self.compile(open(mainf).read())
		executor = SExecutor(code)
		executor.exec()

	def compile(self, scode):
		parser = Parser(scode)
		buff = list(parser.parse())
		code = Code(buff, rules=RULES)
		print(code)
		code.compile()
		print(code)
		return code

	@classmethod
	def this(cls):
		return cls.__this
