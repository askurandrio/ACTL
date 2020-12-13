from actl.syntax.Template import Template
from actl.syntax.AbstractTemplate import AbstractTemplate


class Parsed(AbstractTemplate):
	__slots__ = ('rule',)

	def __init__(self, *templates):
		super().__init__(Template(*templates))

	def __call__(self, parser, buff):
		subParser = parser.subParser(buff.origin)
		subParser.parseLine(insertDefiniton=False)
		parser.definition += subParser.definition
		return self.rule(parser, buff)
