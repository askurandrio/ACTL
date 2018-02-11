
class SyntaxRule:
	def __init__(self, template, func=None, in_context=False):
		from .modules import CustomRule

		self.func = func
		self.in_context = in_context
		self.template = [CustomRule.create(tmpl) for tmpl in template]

	def match(self, code, buff):
		result = ResultMatch(0, False)
		template = iter(self.template)

		for tmpl in template:
			result_rule = tmpl.match(code, buff[result.idx_end:])
			if result_rule:
				result += result_rule
			else:
				return result_rule
		return result

	def __prepare_arguments(self, code, idx_start, idx_end):
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
			return (), kwargs
		if self.in_context:
			return (code, idx_start, idx_end), {}
		return code.buff[idx_start:idx_start+idx_end], {}

	def __contains__(self, item):
		for tmpl in self.template:
			if item not in tmpl:
				return False
		return True

	def __call__(self, code, idx_start, idx_end):
		args, kwargs = self.__prepare_arguments(code, idx_start, idx_end)
		return self.func(*args, **kwargs)

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
	def is_matching(self):
		return bool(self.__idx_end)

	@property
	def is_find(self):
		return bool(self.__is_find)

	@property
	def idx_end(self):
		assert self.__idx_end is not None
		return self.__idx_end

	def __add__(self, other):
		idx_end = self.idx_end if self.is_matching else 0
		idx_end += other.idx_end if other.is_matching else 0
		return type(self)(idx_end, self.is_find or other.is_find)

	def __bool__(self):
		return self.is_find

	def __repr__(self):
		return f'ResultMatch(idx_end={self.__idx_end}, is_find={self.__is_find})'


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
