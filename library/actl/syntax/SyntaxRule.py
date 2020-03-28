from actl.Buffer import Buffer
from actl.syntax.NamedResult import NamedResult
from actl.syntax.Template import Template


class SyntaxRule:
	def __init__(self, template, func, manualApply=False, useParser=False):
		self._template = template
		self.func = func
		self._manualApply = manualApply
		self._useParser = useParser

	def __call__(self, parser, inp):
		res = self._template(parser, inp)
		if res is None:
			return None

		kwargs = {}

		if self._useParser:
			kwargs = {
				**kwargs,
				'parser': parser
			}

		if self._manualApply:
			inp.appFront(*res)
			kwargs = {
				**kwargs,
				'inp': inp
			}
			return self.func(**kwargs)

		args = tuple(arg for arg in res if not isinstance(arg, NamedResult))
		kwargs.update({
			arg.arg: arg.value for arg in res if isinstance(arg, NamedResult)
		})
		return Buffer(self.func(*args, **kwargs))

	def __repr__(self):
		return f'{type(self).__name__}({self._template, self.func})'

	@classmethod
	def wrap(cls, *template, manualApply=False, useParser=False):
		def decorator(func):
			return cls(Template(*template), func, manualApply, useParser)

		return decorator
