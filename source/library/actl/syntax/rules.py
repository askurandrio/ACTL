
from .Template import Template, ResultMatch


class Empty(Template):
	def match(self, scope, buff):
		if buff:
			return ResultMatch(None, False)
		return ResultMatch(0)

	def __repr__(self):
		return f'{type(self).__name__}()'


class OneOpcode(Template):
	def __init__(self, template):
		self.__template = template
		assert opcodes.AnyOpCode == self.__template, f'{opcodes.AnyOpCode} != {self.__template}'

	def match(self, scope, buff):
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

	def match(self, scope, buff):
		for rule in self.__rules:
			result = rule.match(scope, buff)
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

	def match(self, scope, buff):
		result = super().match(scope, buff)
		if result:
			return result
		return ResultMatch(0, True)


class Many(Template):
	def __init__(self, *template, minimum=1):
		self.__minimum = minimum
		super().__init__(*template)

	def match(self, scope, buff):
		result = ResultMatch(0, False)
		for _ in range(self.__minimum):
			result_match = super().match(scope, buff[result.idx_end:])
			if result_match:
				result += result_match
			else:
				return ResultMatch(None, False)
		while True:
			result_match = super().match(scope, buff[result.idx_end:])
			if result_match:
				result += result_match
			else:
				return result
		return ResultMatch(None, False)


class Range(Template):
	def __init__(self, open_template, function, subtemplate=None):
		self.__open_template = Template(*open_template)
		self.__function = function
		if subtemplate is not None:
			subtemplate = Template(*subtemplate)
		self.__subtemplate = subtemplate
		super().__init__(*open_template)

	def match(self, scope, buff):
		result_open = self.__open_template.match(scope, buff)
		if not result_open:
			return ResultMatch(None, False)
		close_template = Template(*self.__function(*buff[:result_open.idx_end]))
		count = 0
		for idx in itertools.count():
			if not buff[idx:]:
				break
			subresult_open = self.__open_template.match(scope, buff[idx:])
			if subresult_open:
				count += 1
				idx += subresult_open.idx_end
			else:
				result_close = close_template.match(scope, buff[idx:])
				if result_close:
					count -= 1
					idx += result_close.idx_end
				else:
					idx += 1
			if not count:
				break
		if count:
			return ResultMatch(idx, False)
		if self.__subtemplate is not None:
			subbuff = buff[result_open.idx_end:idx-result_close.idx_end]
			result_sub = self.__subtemplate.match(scope, subbuff)
			if not result_sub:
				return result_sub.convert_to_false()
		return ResultMatch(idx, True)

	def __repr__(self):
		return super().__repr__()[:-1] + f', {self.__function})'


class Not(Template):
	def __init__(self, *template):
		super().__init__(*template)

	def match(self, scope, buff):
		result = super().match(scope, buff)
		if result:
			return ResultMatch(None, False)
		return ResultMatch(0, True)


class Value(Template):
	def __init__(self, *values):
		self.__values = values
		super().__init__(*(tokens.VARIABLE for _ in self.__values))

	def match(self, scope, buff):
		result = ResultMatch(0, False)

		if not super().match(scope, buff):
			return result

		for idx, value in enumerate(self.__values):
			if scope.get(buff[idx]) != value:
				return ResultMatch(result.idx_end, False)
			result += ResultMatch(1, True)
		return result

	def __repr__(self):
		return f'{type(self).__name__}({self.__values})'


class Stub(Template):
	def __init__(self, function):
		self.__function = function

	def match(self, scope, buff):
		self.__function(scope, buff)
		return ResultMatch(0, True)

	def __repr__(self):
		return f'{type(self).__name__}({self.__function})'
