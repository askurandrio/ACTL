from actl.Buffer import ShiftedBuffer, Buffer
from actl.syntax.Template import Template
from actl.syntax.AbstractTemplate import AbstractTemplate


class Maybe(AbstractTemplate):
	__slots__ = ('template',)

	def __init__(self, *template):
		super().__init__(Template(*template))

	def __call__(self, parser, inp):
		shiftedBuff = ShiftedBuffer(inp)
		res = self.template(parser, shiftedBuff)
		if res is not None:
			inp.shift(shiftedBuff.indexShift)
			return res
		return Buffer()
