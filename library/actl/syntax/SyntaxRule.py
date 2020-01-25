from actl.Buffer import Buffer
from actl.syntax.Template import Template


class SyntaxRule:
	def __init__(self, template, func, manual_apply=False, use_parser=False):
		self._template = template
		self._func = func
		self._manual_apply = manual_apply
		self._use_parser = use_parser

	def __call__(self, parser, inp):
		res = self._template(parser, inp)
		if res is None:
			return None
		kwargs = {}
		if self._use_parser:
			kwargs['parser'] = parser
		if self._manual_apply:
			inp.set_(res + inp)
			self._func(inp, **kwargs)
		else:
			res = self._func(*res, **kwargs)
			inp.set_(Buffer(res) + inp)
		return True

	def __repr__(self):
		return f'{type(self).__name__}({self._template, self._func})'

	@classmethod
	def wrap(cls, *template, manual_apply=False, use_parser=False):
		def decorator(func):
			return cls(Template(*template), func, manual_apply, use_parser)

		return decorator
