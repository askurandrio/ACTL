from actl.Buffer import Buffer
from actl.syntax.NamedResult import NamedResult
from actl.syntax.Template import Template


class SyntaxRule:
	def __init__(self, template, func, manual_apply=False, use_parser=False):
		self._template = template
		self.func = func
		self._manual_apply = manual_apply
		self._use_parser = use_parser

	@property
	def __name__(self):
		return self.func.__name__

	def __call__(self, parser, inp):
		res = self._template(parser, inp)
		if res is None:
			return None
		kwargs = {}
		if self._use_parser:
			kwargs['parser'] = parser
		if self._manual_apply:
			inp.set_(res + inp)
			kwargs = {
				**kwargs,
				'inp': inp
			}
			self.func(**kwargs)
		else:
			args = tuple(arg for arg in res if not isinstance(arg, NamedResult))
			kwargs.update({
				arg.arg: arg.value for arg in res if isinstance(arg, NamedResult)
			})
			res = self.func(*args, **kwargs)
			inp.set_(Buffer(res) + inp)
		return True

	def __repr__(self):
		return f'{type(self).__name__}({self._template, self.func})'

	@classmethod
	def wrap(cls, *template, manual_apply=False, use_parser=False):
		def decorator(func):
			return cls(Template(*template), func, manual_apply, use_parser)

		return decorator
