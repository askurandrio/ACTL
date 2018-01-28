
class SyntaxRule:
	def __init__(self, template, func=None, in_context=False):
		from .modules import CustomRule

		self.func = func
		self.in_context = in_context
		self.template = [CustomRule.create(tmpl) for tmpl in template]

	def match(self, buff):
		result = ResultMatch(0, False)
		template = iter(self.template)

		for tmpl in template:
			result_rule = tmpl.match(buff[result.idx_end:])
			if result_rule:
				result += result_rule
			else:
				return ResultMatch(is_find=False)
		return result

	def __call__(self, code, idx_start, idx_end):
		if hasattr(self.func, 'args'):
			kwargs = {}
			for arg in self.func.args:
				if arg == 'code':
					kwargs['code'] = code
				elif arg == 'idx_start':
					kwargs['idx_start'] = idx_start
				elif arg == 'idx_end':
					kwargs['idx_end'] = idx_end
				elif arg == 'matched_code':
					kwargs['matched_code'] = code.buff[idx_start:idx_start+idx_end]
				else:
					raise RuntimeError(f'This arg not found: {arg}')
			return self.func(**kwargs)
		if self.in_context:
			return self.func(code, idx_start, idx_end)
		return self.func(*code.buff[idx_start:idx_start+idx_end])

	def __repr__(self):
		return f'{type(self).__name__}(func={self.func}, template={self.template})'


class ResultMatch:
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

	def add(self, *template, in_context=False, args=None):
		def decorator(func):
			if args is not None:
				setattr(func, 'args', args)
			self.rules.append(SyntaxRule(template, func, in_context))
			return func
		return decorator

	def __iter__(self):
		return iter(self.rules)

	def __repr__(self):
		return f'SyntaxRules(rules={self.rules})'
