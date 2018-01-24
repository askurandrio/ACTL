
import copy

from .SyntaxRule import SyntaxRule, ResultMath


class OneOpcode(SyntaxRule):
	def __init__(self, template):
		self.__template = template

	def match(self, buff):
		if buff and (self.__template == buff[0]):
			return ResultMath(1)
		return ResultMath(None, False)

	@classmethod
	def create(cls, template):
		if isinstance(template, SyntaxRule):
			return template
		return cls(template)

	def __repr__(self):
		return f'{self.__template}'


class Or(SyntaxRule):
	def __init__(self, *templates):
		self.__rules = []
		for template in templates:
			self.__rules.append(SyntaxRule(template))

	def match(self, buff):
		for rule in self.__rules:
			result = rule.match(buff)
			if result:
				return result
		return ResultMath(None, False)

	def __repr__(self):
		return f'{type(self).__name__}({self.__rules})'
