from actl.Buffer import LTransactionBuffer, Buffer
from actl.syntax.AbstractTemplate import AbstractTemplate
from actl.syntax.Template import Template


class Many(AbstractTemplate):
	__slots__ = ('template', 'minMatches')

	def __init__(self, *template, minMatches=1):
		assert minMatches != 0, f'minMatches<{minMatches}> == 0. Use Maybe for this case'
		super().__init__(Template(*template), minMatches)

	def __call__(self, parser, inp):
		res = Buffer()
		mainLTxInp = LTransactionBuffer(inp)

		for matches in Buffer.inf():
			iterationLTxInp = LTransactionBuffer(mainLTxInp)

			tmplRes = self.template(parser, inp)
			if tmplRes is None:
				if matches < self.minMatches:
					return None

				mainLTxInp.commit()
				return res

			iterationLTxInp.commit()

			res += tmplRes

		raise RuntimeError('Unexpected branch')
