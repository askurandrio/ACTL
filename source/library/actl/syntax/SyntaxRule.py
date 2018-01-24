
class SyntaxRule:
	def __init__(self, template, func=None, in_context=False):
		from .modules import OneOpcode

		self.func = func
		self.in_context = in_context
		self.template = [OneOpcode.create(tmpl) for tmpl in template]

	def match(self, buff):
		result = ResultMath(0, False)
		template = iter(self.template)

		for tmpl in template:
			result_rule = tmpl.match(buff[result.idx_end:])
			if result_rule:
				result += result_rule
			else:
				return ResultMath(is_find=False)
		return result

	def __call__(self, code, idx_start, idx_end):
		if self.in_context:
			return self.func(code, idx_start, idx_end)
		return self.func(code, *code.buff[idx_start:idx_start+idx_end])

	def __repr__(self):
		return f'{type(self).__name__}(func={self.func}, template={self.template})'


class ResultMath:
	def __init__(self, idx_end=None, is_find=None):
		self.__idx_end = idx_end
		self.__is_find = is_find
		if self.__is_find is None:
			assert self.__idx_end is not None
			self.__is_find = True

	@property
	def idx_end(self):
		assert self.__idx_end is not None
		return self.__idx_end

	def __add__(self, other):
		assert other
		if self.__is_find:
			idx_end = self.idx_end
		else:
			idx_end = 0
		return type(self)(other.idx_end + idx_end, True)

	def __bool__(self):
		return self.__is_find


class SyntaxRules:
	def __init__(self):
		self.rules = []

	def add(self, *template, in_context=False):
		def decorator(func):
			self.rules.append(SyntaxRule(template, func, in_context))
			return func
		return decorator

	def __iter__(self):
		return iter(self.rules)

	def __repr__(self):
		return f'SyntaxRules(rules={self.rules})'
