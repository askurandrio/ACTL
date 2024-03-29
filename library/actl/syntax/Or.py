from actl.Buffer import TransactionBuffer
from actl.syntax.Template import Template
from actl.syntax.AbstractTemplate import AbstractTemplate


class Or(AbstractTemplate):
	__slots__ = ('templates',)

	def __init__(self, *templates):
		templates = tuple(Template(*template) for template in templates)
		super().__init__(templates)

	async def __call__(self, parser, inp):
		for template in self.templates:
			transactionBuff = TransactionBuffer(inp)
			res = await template(parser, transactionBuff)
			if res is not None:
				transactionBuff.commit()
				return res

		return None
