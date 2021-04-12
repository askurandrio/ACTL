from actl.Buffer import ShiftedBuffer
from actl.syntax.Template import Template
from actl.syntax.AbstractTemplate import AbstractTemplate


class Or(AbstractTemplate):
	__slots__ = ('templates',)

	def __init__(self, *templates):
		templates = tuple(Template(*template) for template in templates)
		super().__init__(templates)

	def __call__(self, parser, inp):
		for template in self.templates:
			shiftedBuff = ShiftedBuffer(inp)
			res = template(parser, shiftedBuff)
			if res is not None:
				inp.shift(shiftedBuff.indexShift)
				return res

		return None
