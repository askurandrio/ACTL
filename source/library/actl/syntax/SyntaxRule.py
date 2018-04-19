
from .Template import Template


class SyntaxRule(Template):
	def __init__(self, template, func, in_context=False):
		self.__func = func
		self.in_context = in_context
		super().__init__(*template)

	def __prepare_arguments(self, code, idx_start, idx_end):
		if hasattr(self.__func, 'args'):
			args = []
			for key in self.__func.args:
				if key == 'code':
					args.append(code)
				elif key == 'idx_start':
					args.append(idx_start)
				elif key == 'idx_end':
					args.append(idx_end)
				elif key == 'matched_code':
					args.append(list(code[idx_start:idx_start+idx_end]))
				else:
					raise RuntimeError(f'This key not found: {key}')
		elif self.in_context:
			args = code, idx_start, idx_end
		else:
			args = code[idx_start:idx_start+idx_end]
		return args

	def __call__(self, code, idx_start, idx_end):
		args = self.__prepare_arguments(code, idx_start, idx_end)
		return self.__func(*args)

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
