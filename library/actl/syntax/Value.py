from actl.Buffer import Buffer
from actl.opcodes import VARIABLE
from actl.syntax.AbstractTemplate import AbstractTemplate


class Value(AbstractTemplate):
	__slots__ = ('value',)

	async def __call__(self, parser, buff):
		if (
			(not buff)
			or (VARIABLE != buff[0])
			or (parser.scope.get(buff[0].name) != self.value)
		):
			return None

		return Buffer.of(buff.pop())
