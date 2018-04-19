
from .Template import Template


class SyntaxRule(Template):
	def __init__(self, template, func, in_context=False):
		self.__func = func
		self.in_context = in_context
		super().__init__(*template)

	def __prepare_arguments(self, code, idx_start, idx_end):
		if hasattr(self.__func, 'args'):
			kwargs = {}
			for arg in self.__func.args:
				if arg == 'code':
					kwargs['code'] = code
				elif arg == 'idx_start':
					kwargs['idx_start'] = idx_start
				elif arg == 'idx_end':
					kwargs['idx_end'] = idx_end
				elif arg == 'matched_code':
					kwargs['matched_code'] = list(code[idx_start:idx_start+idx_end])
				else:
					raise RuntimeError(f'This arg not found: {arg}')
			return (), kwargs
		if self.in_context:
			return (code, idx_start, idx_end), {}
		return list(code[idx_start:idx_start+idx_end]), {}

	def __call__(self, code, idx_start, idx_end):
		args, kwargs = self.__prepare_arguments(code, idx_start, idx_end)
		return self.__func(*args, **kwargs)

	def __repr__(self):
		return super().__repr__()[:-1] + f', {self.__func}, {self.in_context})'


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
