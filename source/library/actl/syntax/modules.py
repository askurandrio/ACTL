
import itertools

from .SyntaxRule import SyntaxRule, ResultMath


class CustomRule:
	def __init__(self, func, name=None):
		self.__name = name
		self.__func = func

	@property
	def match(self):
		return self.__func

	@classmethod
	def create(cls, template):
		if isinstance(template, cls) or isinstance(template, SyntaxRule):
			return template
		return OneOpcode(template)

	def __repr__(self):
		name = self.__func if self.__name is None else self.__name
		return f'CustomRule({name})'


def OneOpcode(template):
	def func(buff):
		if buff and (template == buff[0]):
			return ResultMath(1)
		return ResultMath(None, False)
	return CustomRule(func, f'OneOpcode({template}')


def Or(*templates):
	rules = [SyntaxRule(template) for template in templates]
	def func(buff):
		for rule in rules:
			result = rule.match(buff)
			if result:
				return result
		return ResultMath(None, False)
	return CustomRule(func, f'Or({templates}')


def Maybe(*template):
	rule = SyntaxRule(template)
	def func(buff):
		result = rule.match(buff)
		if result:
			return result
		return ResultMath(0, True)
	return CustomRule(func, f'Maybe({template}')


def Many(*template, minimum=1):
	assert minimum
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
	return CustomRule(func, f'Many({template})')


def Range(open_template, function):
	open_rule = SyntaxRule(open_template)
	def func(buff):
		result_match = open_rule.match(buff)
		if not result_match:
			return ResultMath(None, False)
		close_rule = SyntaxRule(function(*buff[:result_match.idx_end]))
		count = 0
		for idx in itertools.count():
			if not buff[idx:]:
				break
			if open_rule.match(buff[idx:]):
				count += 1
			if close_rule.match(buff[idx:]):
				count -= 1
			if not count:
				break
		result_match = close_rule.match(buff[idx:])
		if result_match:
			idx += result_match.idx_end
		assert not count
		return ResultMath(idx, True)
	return CustomRule(func)


def Stub(function):
	def func(buff):
		function(buff)
		return ResultMath(0, True)
	return CustomRule(func, f'Stub({function})')
