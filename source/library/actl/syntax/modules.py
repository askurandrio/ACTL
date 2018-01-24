
from .SyntaxRule import SyntaxRule, ResultMath


class CustomRule:
	def __init__(self, func):
		self.__func = func

	def match(self, buff):
		return self.__func(buff)

	@classmethod
	def create(cls, template):
		if isinstance(template, cls) or isinstance(template, SyntaxRule):
			return template
		return OneOpcode(template)


def OneOpcode(template):
	def func(buff):
		if buff and (template == buff[0]):
			return ResultMath(1)
		return ResultMath(None, False)
	return CustomRule(func)


def Or(*templates):
	rules = [SyntaxRule(template) for template in templates]
	def func(buff):
		for rule in rules:
			result = rule.match(buff)
			if result:
				return result
		return ResultMath(None, False)
	return CustomRule(func)


def Maybe(*template):
	rule = SyntaxRule(template)
	def func(buff):
		result = rule.match(buff)
		if result:
			return result
		return ResultMath(0, True)
	return CustomRule(func)


def Many(*template, minimum=0):
	rule = SyntaxRule(template)
	def func(buff):
		result = ResultMath(0, False)
		for _ in range(minimum):
			result_match = rule.match(buff[result.idx_end:])
			if result_match:
				result += result_match
			else:
				return ResultMath(None, False)
		while True:
			result_match = rule.match(buff[result.idx_end:])
			if result_match:
				result += result_match
			else:
				return result
	return CustomRule(func)
