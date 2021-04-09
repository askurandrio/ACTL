from inspect import isclass
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
			inp.insert(0, res)
			kwargs = {
				**kwargs,
				'inp': inp
			}
			self.func(**kwargs)
			return True

		args = tuple(arg for arg in res if not isinstance(arg, NamedResult))
		kwargs.update({
			arg.arg: arg.value for arg in res if isinstance(arg, NamedResult)
		})
		res = self.func(*args, **kwargs)
		inp.insert(0, res)
		return bool(res)

	def __repr__(self):
		return f'{type(self).__name__}({self._template, self.func})'

	@classmethod
	def wrap(cls, *template, manualApply=False, useParser=False):
		def decorator(func):
			if isclass(func):
				class_ = func

				def func(*args, **kwargs):
					instance = class_(*args, **kwargs)
					return instance.parse()

			return cls(Template(*template), func, manualApply, useParser)

		return decorator
