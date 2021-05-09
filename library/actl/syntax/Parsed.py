from actl.syntax import BufferRule
from actl.syntax.Template import Template
from actl.syntax.AbstractTemplate import AbstractTemplate


class Parsed(AbstractTemplate):
	__slots__ = ('until', 'checkEndLineInBuff', 'withEnd')

	def __init__(self, *templates, checkEndLineInBuff=False, withEnd=False):
		if templates:
			until = Template(*templates)
		else:
			until = None
		super().__init__(until, checkEndLineInBuff, withEnd)

	def __call__(self, parser, buff):
		subParser = parser.subParser(buff.origin, self.until)
		if self.until is None:
			subParser.parseLine(insertDefiniton=False)
			parser.definition += subParser.definition
			return ()

		subParser.parseLine(checkEndLineInBuff=self.checkEndLineInBuff)
		bufferRule = BufferRule(parser, buff)
		res = bufferRule.popUntil(self.until)
		if self.withEnd:
			res += bufferRule.pop(self.until)
		return tuple(res)
