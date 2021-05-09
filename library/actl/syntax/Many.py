from actl.Buffer import TransactionBuffer, Buffer
from actl.syntax.AbstractTemplate import AbstractTemplate
from actl.syntax.Template import Template


class Many(AbstractTemplate):
	__slots__ = ('template', 'minMatches')

	def __init__(self, *template, minMatches=1):
		super().__init__(Template(*template), minMatches)

	def __call__(self, parser, inp):
		res = Buffer()
		mainTransactionBuff = TransactionBuffer(inp)

		for matches in Buffer.inf():
			itTransactionBuff = TransactionBuffer(mainTransactionBuff)

			tmplRes = self.template(parser, inp)
			if tmplRes is None:
				if matches < self.minMatches:
					return None

				mainTransactionBuff.commit()
				return res

			itTransactionBuff.commit()

			res += tmplRes

		raise RuntimeError('Unexpected branch')
