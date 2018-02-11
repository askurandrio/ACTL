
import itertools

from ..code import opcodes
from ..parser import tokens
from .SyntaxRule import SyntaxRule, ResultMatch


class CustomRule:
	def __init__(self, func, name=None, contains=None):
		self.__name = name
		self.__func = func
		if contains is None:
			contains = lambda item: False
		self.__contains = contains

	@property
	def match(self):
		return self.__func

	@classmethod
	def create(cls, template):
		if isinstance(template, cls) or isinstance(template, SyntaxRule):
			return template
		return OneOpcode(template)

	@property
	def __contains__(self):
		return self.__contains

	def __repr__(self):
		name = self.__func if self.__name is None else self.__name
		return f'CustomRule({name})'


def OneOpcode(template):
	assert opcodes.AnyOpCode == template

	def func(code, buff):
		if buff and (template == buff[0]):
			return ResultMatch(1)
		return ResultMatch(None, False)

	def contains(item):
		return template == item

	return CustomRule(func, f'OneOpcode({template}', contains)


def Or(*templates):
	rules = [SyntaxRule(template) for template in templates]

	def func(code, buff):
		for rule in rules:
			result = rule.match(code, buff)
			if result:
				return result
		return ResultMatch(None, False)

	def contains(item):
		for rule in rules:
			if item not in rule:
				return False
		return True

	return CustomRule(func, f'Or({templates}', contains)


def Maybe(*template):
	rule = SyntaxRule(template)

	def func(code, buff):
		result = rule.match(code, buff)
		if result:
			return result
		return ResultMatch(0, True)

	def contains(item):
		return item in rule

	return CustomRule(func, f'Maybe({template}', contains)


def Many(*template, minimum=1):
	assert minimum
	rule = SyntaxRule(template)

	def func(code, buff):
		result = ResultMatch(0, False)
		for _ in range(minimum):
			result_match = rule.match(code, buff[result.idx_end:])
			if result_match:
				result += result_match
			else:
				return ResultMatch(None, False)
		while True:
			result_match = rule.match(code, buff[result.idx_end:])
			if result_match:
				result += result_match
			else:
				return result

	def contains(item):
		return item in rule

	return CustomRule(func, f'Many({template})', contains)


def Range(open_template, function):
	open_rule = SyntaxRule(open_template)

	def func(code, buff):
		result_match = open_rule.match(code, buff)
		if not result_match:
			return ResultMatch(None, False)
		close_rule = SyntaxRule(function(*buff[:result_match.idx_end]))
		count = 0
		for idx in itertools.count():
			if not buff[idx:]:
				break
			if open_rule.match(code, buff[idx:]):
				count += 1
			if close_rule.match(code, buff[idx:]):
				count -= 1
				if not count:
					idx += 1
			if not count:
				break
		result_match = close_rule.match(code, buff[idx:])
		if result_match:
			idx += result_match.idx_end
		assert not count
		return ResultMatch(idx, True)

	def contains(item):
		return item in open_rule

	return CustomRule(func, f'Range({open_template}, {function}', contains)


def Not(*template):
	rule = SyntaxRule(template)

	def func(code, buff):
		result = rule.match(code, buff)
		if result:
			return ResultMatch(None, False)
		return ResultMatch(0, True)

	return CustomRule(func, f'Not({template}')


def Value(*values):
	def func(code, buff):
		result = ResultMatch(0, False)
		for idx, value in enumerate(values):
			if not buff[result.idx_end:]:
				return ResultMatch(result.idx_end, False)
			if (tokens.VARIABLE != buff[idx]) or (code.scope.get(buff[idx]) != value):
				return ResultMatch(result.idx_end, False)
			result += ResultMatch(1, True)
		return result
	return CustomRule(func, f'VALUE({values})')


def ToSpecific(*template):
	rule = SyntaxRule(template)

	def __func(code, buff):
		result = ResultMatch(0, False)
		while buff[result.idx_end:]:
			result_match = rule.match(code, buff[result.idx_end:])
			if result_match:
				result += result_match
				return result
			else:
				result += ResultMatch(1, False)
		return ResultMatch(result.idx_end, False)

	def get_max(code, buff):
		max_idx = -1
		for crule in code.rules:
			if rule in crule:
				result = crule.match(code, buff)
				if result and (result.idx_end > max_idx):
					max_idx = result.idx_end
		return max_idx

	def func(code, buff):
		result = ResultMatch(0, False)
		while buff[result.idx_end:]:
			midx_end = get_max(code, buff[result.idx_end:])
			if midx_end == -1:
				result += __func(code, buff)
				return result
			else:
				result += ResultMatch(result.idx_end+midx_end, False)
		return ResultMatch(result.idx_end, False)

	def contains(item):
		return item in rule

	return CustomRule(func, f'ToSpecific({template})', contains)


def Stub(function):
	def func(code, buff):
		function(buff)
		return ResultMatch(0, True)
	return CustomRule(func, f'Stub({function})')
