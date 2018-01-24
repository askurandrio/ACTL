
from ..code.Code import Code
from ..parser import Parser
from ..syntax.rules import RULES


class Project:
	__this = None

	def __init__(self):
		self.__class__.__this = self

	def parse(self, filename=None, string=None):
		if filename is not None:
			string = open(filename, encoding='utf8').read()
		return Parser(string).parse()

	def compile(self, filename=None, string=None, code=None):
		from pyport import Scope, SExecutor

		parser = self.parse(filename, string)
		if code is None:
			buff = list(parser)
			code = Code(buff, RULES, Scope())
			print(code)
		sexecutor = SExecutor(code, code.scope)
		sexecutor.execute()
		from actl.TranslateToString import TranslateToString
		tr = TranslateToString()
		tr.translate(code)
		print(tr.string)

	@classmethod
	def this(cls):
		return cls.__this
