from actl.Buffer import Buffer
from actl.syntax import BufferRule
from actl.syntax.Template import Template
from actl.syntax.AbstractTemplate import AbstractTemplate


class Frame(AbstractTemplate):
	__slots__ = ('until',)

	def __init__(self, *templates):
		super().__init__(Template(*templates))

	def __call__(self, parser, buff):
		parser.subParser(buff.origin, self.until).parseLine()
		res = BufferRule(parser, buff).popUntil(self.until)
		return tuple(res)
