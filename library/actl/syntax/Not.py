from actl.Buffer import ShiftedBuffer
from actl.syntax.Template import Template
from actl.syntax.AbstractTemplate import AbstractTemplate


class Not(AbstractTemplate):
	__slots__ = ('template',)

	def __call__(self, parser, inp):
		shiftedBuff = ShiftedBuffer(inp)
		res = self.template(parser, shiftedBuff)
		if res is None:
			return ()
		return None
