
from .Template import Template


class SyntaxRules:
	def __init__(self):
		self._rules = []

	def add(self, *template, manual_apply=False, use_parser=False):
		def decorator(func):
			self._rules.append(_SyntaxRule(Template(*template), func, manual_apply, use_parser))
			return func
		return decorator

	def __iter__(self):
		return iter(self._rules)

	def __repr__(self):
		return f'{type(self).__name__}(rules={self._rules})'
	

class _SyntaxRule:
	def __init__(self, template, func, manual_apply, use_parser):
		self._template = template
		self._func = func
		self._manual_apply = manual_apply
		self._use_parser = use_parser
	
	def __call__(self, inp):
		buff = inp.copy()
		res = self._template(buff)
		if not res:
			return None
		if self._manual_apply:
			return _ResultManualApply(self._func, self._use_parser, inp)
		return _Result(self._func, self._use_parser, inp, buff, res)

	def __repr__(self):
		return f'{type(self).__name__}({self._template, self._func})'


class _ResultManualApply:
	def __init__(self, func, use_parser, inp):
		self._func = func
		self._inp = inp
		self._use_parser = use_parser

	def __call__(self, parser):
		kwargs = {}
		if self._use_parser:
			kwargs['parser'] = parser
		self._func(self._inp, **kwargs)


class _Result(_ResultManualApply):
	def __init__(self, func, use_parser, inp, buff, res):
		super().__init__(func, use_parser, inp)
		self._buff = buff
		self._res = res

	def __call__(self, parser):
		self._inp[:] = self._buff
		kwargs = {}
		if self._use_parser:
			kwargs['parser'] = parser
		self._inp[:0] = self._func(*self._res, **kwargs)
