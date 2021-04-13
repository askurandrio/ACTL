from actl.syntax.AbstractTemplate import AbstractTemplate


class _BreakPoint(AbstractTemplate):
	__slots__ = ()

	def __call__(self, parser, inp):
		breakpoint()
		return ()


BreakPoint = _BreakPoint()
