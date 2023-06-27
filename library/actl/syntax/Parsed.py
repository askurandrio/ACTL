from actl.syntax import BufferRule
from actl.syntax.CustomTemplate import End
from actl.syntax.Template import Template
from actl.syntax.Or import Or
from actl.syntax.AbstractTemplate import AbstractTemplate
from actl.Buffer import Buffer


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

		await subParser.parseUntilLineEnd(insertDefiniton=False)
		parser.definition += subParser.definition

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
			await subParser.parseUntilLineEnd(insertDefiniton=False)
			parser.definition += subParser.definition
			return ()

		await subParser.parseUntilLineEnd(checkEndLineInBuff=self.checkEndLineInBuff)
		res = await Buffer.loadAsync(BufferRule(parser, buff).popUntil(self.until))
		return tuple(res)


class MatchParsedOld(ParsedOld):
	def __init__(self, *templates):
		super().__init__(Or(templates, [End]), checkEndLineInBuff=True)

	async def __call__(self, parser, buff):
		res = await super().__call__(parser, buff)
		if res:
			return None

		buff = BufferRule(parser, buff)
		if await buff.startsWith(self.until):
			return await buff.pop(self.until)

		return None
