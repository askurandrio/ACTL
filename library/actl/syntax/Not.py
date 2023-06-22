from actl.Buffer import TransactionBuffer
from actl.syntax.Template import Template
from actl.syntax.AbstractTemplate import AbstractTemplate


class Not(AbstractTemplate):
	__slots__ = ('template',)

	def __init__(self, *template):
		super().__init__(Template(*template))

	async def __call__(self, parser, inp):
		transactionBuff = TransactionBuffer(inp)
		res = await self.template(parser, transactionBuff)
		if res is None:
			return ()
		return None
