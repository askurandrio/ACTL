from actl.syntax.AbstractTemplate import AbstractTemplate


class _BreakPoint(AbstractTemplate):
	__slots__ = ()

	async def __call__(self, parser, inp):
		breakpoint()  # pylint: disable=forgotten-debug-statement
		return ()


BreakPoint = _BreakPoint()
