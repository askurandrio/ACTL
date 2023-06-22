from inspect import isclass

from actl.syntax.NamedResult import NamedResult
from actl.syntax.Template import Template
from actl.utils import setFunctionName


class SyntaxRule:
	def __init__(self, runTemplate, func, manualApply=False, useParser=False):
		self._runTemplate = runTemplate
		self.func = func
		self._manualApply = manualApply
		self._useParser = useParser

	async def match(self, parser, inp):
		res = await self._runTemplate(parser, inp)
		if res is None:
			return None

		async def apply():
			nonlocal res, inp

			kwargs = {}

			if self._useParser:
				kwargs = {**kwargs, 'parser': parser}

			if self._manualApply:
				inp.insert(0, res)
				kwargs = {**kwargs, 'inp': inp}
				await self.func(**kwargs)
				return

			args = tuple(arg for arg in res if not isinstance(arg, NamedResult))
			kwargs.update(
				{arg.arg: arg.value for arg in res if isinstance(arg, NamedResult)}
			)
			try:
				res = await self.func(*args, **kwargs)
			except:
				print(self)
				raise
			while hasattr(inp, 'origin'):
				inp = inp.origin
			inp.insert(0, res)

		apply = setFunctionName(apply, f'SyntaRule__{self.func.__name__}__apply')
		return apply

	def __repr__(self):
		return f'{type(self).__name__}({self._runTemplate.template, self.func})'

	@classmethod
	def wrap(cls, *template, manualApply=False, useParser=False):
		def decorator(userFunc):
			nonlocal template

			if isclass(userFunc):

				async def func(*args, **kwargs):
					instance = userFunc(*args, **kwargs)
					return await instance.parse()

				func = setFunctionName(func, userFunc.__name__)
			else:
				func = userFunc

			template = Template(*template)
			runTemplate = setFunctionName(
				template.__call__, f'{userFunc.__name__}Template'
			)
			runTemplate.template = template

			return cls(runTemplate, func, manualApply, useParser)

		return decorator
