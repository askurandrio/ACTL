from inspect import isclass
from actl.syntax.NamedResult import NamedResult
from actl.syntax.Template import Template


class SyntaxRule:
	def __init__(self, template, func, manualApply=False, useParser=False):
		self._template = template
		self.func = func
		self._manualApply = manualApply
		self._useParser = useParser

	def match(self, parser, inp):
		res = self._template(parser, inp)
		if res is None:
			return None

		def apply():
			nonlocal res, inp

			kwargs = {}

			if self._useParser:
				kwargs = {**kwargs, 'parser': parser}

			if self._manualApply:
				inp.insert(0, res)
				kwargs = {**kwargs, 'inp': inp}
				self.func(**kwargs)
				return

			args = tuple(arg for arg in res if not isinstance(arg, NamedResult))
			kwargs.update(
				{arg.arg: arg.value for arg in res if isinstance(arg, NamedResult)}
			)
			res = self.func(*args, **kwargs)
			while hasattr(inp, 'origin'):
				inp = inp.origin
			inp.insert(0, res)

		return apply

	def __repr__(self):
		return f'{type(self).__name__}({self._template, self.func})'

	@classmethod
	def wrap(cls, *template, manualApply=False, useParser=False):
		def decorator(userFunc):
			if isclass(userFunc):

				def func(*args, **kwargs):
					instance = userFunc(*args, **kwargs)
					return instance.parse()

			else:
				func = userFunc

			return cls(Template(*template), func, manualApply, useParser)

		return decorator
