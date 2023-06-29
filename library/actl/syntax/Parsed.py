from actl.syntax import BufferRule
from actl.syntax.CustomTemplate import End
from actl.syntax.Template import Template
from actl.syntax.Or import Or
from actl.syntax.AbstractTemplate import AbstractTemplate
from actl.Buffer import Buffer
from actl.utils import loadCoroutine


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


class ParsedOld(AbstractTemplate):
	__slots__ = ('until', 'checkEndLineInBuff')

	def __init__(self, *templates, checkEndLineInBuff=False):
		if templates:
			until = Template(*templates)
		else:
			until = None
		super().__init__(until, checkEndLineInBuff)

	async def __call__(self, parser, buff):
		origin = getattr(buff, 'origin', buff)
		subParser = parser.subParser(origin, self.until)
		if self.until is None:
			await subParser.parseUntilLineEnd()
			return ()

		definition, _ = loadCoroutine(
			subParser.parseUntilLineEnd(checkEndLineInBuff=self.checkEndLineInBuff)
		)
		origin.insert(0, definition)
		res = await Buffer.loadAsync(BufferRule(parser, buff).popUntil(self.until))
		return tuple(res)
