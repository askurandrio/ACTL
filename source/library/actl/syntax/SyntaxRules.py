
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
	
	def __call__(self, inp):
		buff = inp.copy()
		res = self._template(buff)
		if not res:
			return None
		return _Result(self._func, inp, buff, res)

	def __repr__(self):
		return f'{type(self).__name__}({self._template, self._func})'


class _Result:
	def __init__(self, func, inp, buff, res):
		self._func = func
		self._inp = inp
		self._buff = buff
		self._res = res

	def __call__(self):
		self._inp.set(self._buff)
		self._inp[:0] = self._func(*self._res)
