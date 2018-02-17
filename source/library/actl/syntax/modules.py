
import itertools

from ..code import opcodes
from ..parser import tokens
from .Template import Template, ResultMatch


class OneOpcode(Template):
	def __init__(self, template):
		self.__template = template
		assert opcodes.AnyOpCode == self.__template, f'{opcodes.AnyOpCode} != {self.__template}'

	def match(self, code, buff):
		if buff and (self.__template == buff[0]):
			return ResultMatch(1)
		return ResultMatch(None, False)

	def __contains__(self, item):
		return self.__template == item

	def __repr__(self):
		return f'{type(self).__name__}({self.__template})'


class Or(Template):
	def __init__(self, *templates):
		self.__rules = [Template(*template) for template in templates]

	def match(self, code, buff):
		for rule in self.__rules:
			result = rule.match(code, buff)
			if result:
				return result
		return ResultMatch(None, False)

	def __contains__(self, item):
		for rule in self.__rules:
			if item not in rule:
				return False
		return True

	def __repr__(self):
		return f'{type(self).__name__}({self.__rules})'


class Maybe(Template):
	def __init__(self, *template):
		super().__init__(*template)

	def match(self, code, buff):
		result = super().match(code, buff)
		if result:
			return result
		return ResultMatch(0, True)


class Many(Template):
	def __init__(self, *template, minimum=1):
		self.__minimum = minimum
		assert self.__minimum
		super().__init__(*template)

	def match(self, code, buff):
		result = ResultMatch(0, False)
		for _ in range(self.__minimum):
			result_match = super().match(code, buff[result.idx_end:])
			if result_match:
				result += result_match
			else:
				return ResultMatch(None, False)
		while True:
			result_match = super().match(code, buff[result.idx_end:])
			if result_match:
				result += result_match
			else:
				return result
		return ResultMatch(None, False)


class Range(Template):
	def __init__(self, open_template, function):
		self.__function = function
		super().__init__(*open_template)

	def match(self, code, buff):
		result_match = super().match(code, buff)
		if not result_match:
			return ResultMatch(None, False)
		close_rule = Template(*self.__function(*buff[:result_match.idx_end]))
		count = 0
		for idx in itertools.count():
			if not buff[idx:]:
				break
			if super().match(code, buff[idx:]):
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

	def __repr__(self):
		return super().__repr__()[:-1] + f', {self.__function})'


class Not(Template):
	def __init__(self, *template):
		super().__init__(*template)

	def match(self, code, buff):
		result = super().match(code, buff)
		if result:
			return ResultMatch(None, False)
		return ResultMatch(0, True)


class Value(Template):
	def __init__(self, *values):
		self.__values = values
		super().__init__(*(tokens.VARIABLE for _ in self.__values))

	def match(self, code, buff):
		result = ResultMatch(0, False)

		if not super().match(code, buff):
			return result

		for idx, value in enumerate(self.__values):
			if code.scope.get(buff[idx]) != value:
				return ResultMatch(result.idx_end, False)
			result += ResultMatch(1, True)
		return result

	def __repr__(self):
		return f'{type(self).__name__}({self.__values})'


class ToSpecific(Template):
	def __init__(self, *template):
		super().__init__(*template)

	def match(self, code, buff):
		result = ResultMatch(0, False)
		while buff[result.idx_end:]:
			midx_end = self.__get_max(code, buff[result.idx_end:])
			if midx_end == -1:
				result += self.__func(code, buff)
				return result
			else:
				result += ResultMatch(result.idx_end+midx_end, False)
		return ResultMatch(result.idx_end, False)
	
	def __get_max(self, code, buff):
		max_idx = -1
		for crule in code.rules:
			if self in crule:
				result = crule.match(code, buff)
				if result and (result.idx_end > max_idx):
					max_idx = result.idx_end
		return max_idx

	def __func(self, code, buff):
		result = ResultMatch(0, False)
		while buff[result.idx_end:]:
			result_match = super().match(code, buff[result.idx_end:])
			if result_match:
				result += result_match
				return result
			else:
				result += ResultMatch(1, False)
		return ResultMatch(result.idx_end, False)


class Stub(Template):
	def __init__(self, function):
		self.__function = function

	def match(self, code, buff):
		self.__function(buff)
		return ResultMatch(0, True)

	def __repr__(self):
		return f'{type(self).__name__}({self.__function})'
