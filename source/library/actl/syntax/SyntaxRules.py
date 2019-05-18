
from .Template import Template


class SyntaxRules:
	def __init__(self):
		self._rules = []

	def add(self, *template, manual_apply=False):
		def decorator(func):
			self._rules.append(_SyntaxRule(Template(*template), func, manual_apply))
			return func
		return decorator

	def __iter__(self):
		return iter(self._rules)

	def __repr__(self):
		return f'{type(self).__name__}(rules={self._rules})'
	

class _SyntaxRule:
	def __init__(self, template, func, manual_apply):
		self._template = template
		self._func = func
		self._manual_apply = manual_apply
	
	def __call__(self, inp):
		buff = inp.copy()
		res = self._template(buff)
		if not res:
			return None
		if self._manual_apply:
			return _ResultManualApply(self._func, inp)
		return _Result(self._func, inp, buff, res)

	def __repr__(self):
		return f'{type(self).__name__}({self._template, self._func})'


class _ResultManualApply:
	def __init__(self, func, inp):
		self._func = func
		self._inp = inp

	def __call__(self, parser):
		self._func(self._inp, parser)


class _Result(_ResultManualApply):
	def __init__(self, func, inp, buff, res):
		super().__init__(func, inp)
		self._buff = buff
		self._res = res

	def __call__(self, _):
		self._inp.set(self._buff)
		self._inp[:0] = self._func(*self._res)
