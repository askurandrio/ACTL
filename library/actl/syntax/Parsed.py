from actl.syntax import BufferRule
from actl.syntax.Template import Template
from actl.syntax.AbstractTemplate import AbstractTemplate


class Parsed(AbstractTemplate):
	__slots__ = ('until',)

	def __init__(self, *templates):
		if templates:
			until = Template(*templates)
		else:
			until = None
		super().__init__(until)

	def __call__(self, parser, buff):
		subParser = parser.subParser(buff.origin, self.until)
		if self.until is None:
			subParser.parseLine(insertDefiniton=False)
			parser.definition += subParser.definition
			return ()

		subParser.parseLine()
		res = BufferRule(parser, buff).popUntil(self.until)
		return tuple(res)
