from actl.syntax import BufferRule
from actl.syntax.CustomTemplate import End
from actl.syntax.Template import Template
from actl.syntax.Or import Or
from actl.syntax.AbstractTemplate import AbstractTemplate


class Parsed(AbstractTemplate):
	__slots__ = ('until', 'checkEndLineInBuff')

	def __init__(self, *templates, checkEndLineInBuff=False):
		if templates:
			until = Template(*templates)
		else:
			until = None
		super().__init__(until, checkEndLineInBuff)

	def __call__(self, parser, buff):
		origin = getattr(buff, 'origin', buff)
		subParser = parser.subParser(origin, self.until)
		if self.until is None:
			subParser.parseUntilLineEnd(insertDefiniton=False)
			parser.definition += subParser.definition
			return ()

		subParser.parseUntilLineEnd(checkEndLineInBuff=self.checkEndLineInBuff)
		res = BufferRule(parser, buff).popUntil(self.until)
		return tuple(res)


class MatchParsed(Parsed):
	def __init__(self, *templates):
		super().__init__(Or(templates, [End]), checkEndLineInBuff=True)

	def __call__(self, parser, buff):
		res = super().__call__(parser, buff)
		if res:
			return None

		buff = BufferRule(parser, buff)
		if buff.startsWith(self.until):
			return buff.pop(self.until)

		return None
