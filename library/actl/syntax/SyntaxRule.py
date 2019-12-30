from actl.syntax.Template import Template


class SyntaxRule:
	def __init__(self, template, func, manual_apply=False, use_parser=False):
		self._template = template
		self._func = func
		self._manual_apply = manual_apply
		self._use_parser = use_parser

	def __call__(self, scope, inp):
		res = self._template(scope, inp.copy())
		if res is None:
			return None
		if self._manual_apply:
			return _ResultManualApply(self._func, self._use_parser, inp)
		return _Result(self._func, self._use_parser, inp, res)

	def __repr__(self):
		return f'{type(self).__name__}({self._template, self._func})'

	@classmethod
	def wrap(cls, *template, manual_apply=False, use_parser=False):
		def decorator(func):
			return cls(Template(*template), func, manual_apply, use_parser)

		return decorator


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
	def __init__(self, func, use_parser, inp, res):
		def apply(self_inp, **kwargs):
			del self_inp[:len(res)]
			self_inp[:0] = func(*res, **kwargs)

		super().__init__(apply, use_parser, inp)
