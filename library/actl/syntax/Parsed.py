from actl.syntax import BufferRule
from actl.syntax.Template import Template
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
			subParser.parseLine(insertDefiniton=False)
			parser.definition += subParser.definition
			return ()

		subParser.parseLine(checkEndLineInBuff=self.checkEndLineInBuff)
		res = BufferRule(parser, buff).popUntil(self.until)
		return tuple(res)
