
from .Template import Template


class SyntaxRules:
	def __init__(self):
		self._rules = []

	def add(self, *template):
		def decorator(func):
			self._rules.append(_SyntaxRule(Template(*template), func))
			return func
		return decorator

	def __iter__(self):
		return iter(self._rules)

	def __repr__(self):
		return f'{type(self).__name__}(rules={self._rules})'


class _SyntaxRule:
	def __init__(self, template, func):
		self._template = template
		self._func = func
	
	def __call__(self, buff):
		res = self._template(buff)
		if not res:
			return res
		return _Result(self._func, res.idx_end)


class _Result:
	def __init__(self, func, idx_end):
		self.func = func
		self.idx_end = idx_end

	def __call__(self, buff):
		tokens = buff[:self.idx_end]
		del buff[:self.idx_end]
		res = self.func(*tokens)
		buff[:0] = res
