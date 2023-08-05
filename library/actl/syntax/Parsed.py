from actl.syntax import BufferRule
from actl.syntax.CustomTemplate import End
from actl.syntax.Template import Template
from actl.syntax.Or import Or
from actl.syntax.AbstractTemplate import AbstractTemplate
from actl.Buffer import Buffer
from actl.utils import loadCoroutine


class _Until(AbstractTemplate):
	__slots__ = ('until',)

	def __init__(self, *until):
		self.until = Template(*until)

	async def __call__(self, parser, inp):
		result = Buffer()
		bufferRule = BufferRule(parser, inp)

		while inp and (not await bufferRule.startsWith(self.until)):
			result.append(inp.pop(0))

		return result


class Parsed(AbstractTemplate):
	__slots__ = ('template', 'endLine')

	def __init__(self, *template, endLine=None):
		template = Template(*template)

		if endLine is not None:
			endLine = Template(*endLine)

		super().__init__(template, endLine)

	async def __call__(self, parser, buff):
		origin = getattr(buff, 'origin', buff)
		subParser = parser.subParser(origin, self.endLine)
		await subParser.parseUntilLineEnd()
		return await self.template(parser, buff)

	@classmethod
	def until(cls, endLine):
		return cls(_Until(endLine), endLine=[endLine])
