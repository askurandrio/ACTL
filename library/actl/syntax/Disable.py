from actl.syntax.AbstractTemplate import AbstractTemplate
from actl.syntax.Template import Template


class Disable(AbstractTemplate):
	__slots__ = ('rules', 'template')

	def __init__(self, rules, template):
		self.rules = rules
		self.template = Template(*template)

	async def __call__(self, parser, inp):
		with parser.rules.disable(*self.rules):
			return await self.template(parser, inp)
