from actl.Buffer import ShiftedBuffer
from actl.syntax.Template import Template
from actl.syntax.AbstractTemplate import AbstractTemplate


class And(AbstractTemplate):
	__slots__ = ('templates',)

	def __init__(self, *templates):
		templates = tuple(Template(*template) for template in templates)
		super().__init__(templates)

	def __call__(self, parser, inp):
		maxShiftIndex = 0 

		for template in self.templates:
			shiftedBuff = ShiftedBuffer(inp)
			res = template(parser, shiftedBuff)
			if res is None:
				return None
			maxShiftIndex = max(maxShiftIndex, res.shiftIndex)

		res = inp[:maxShiftIndex]
		inp.shift(maxShiftIndex)
		return res
