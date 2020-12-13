from actl.Buffer import LTransactionBuffer, Buffer
from actl.syntax.Template import Template
from actl.syntax.AbstractTemplate import AbstractTemplate


class Maybe(AbstractTemplate):
	__slots__ = ('template',)

	def __init__(self, *template):
		super().__init__(Template(*template))

	def __call__(self, parser, inp):
		lTxInp = LTransactionBuffer(inp)
		res = self.template(parser, inp)
		if res is not None:
			lTxInp.commit()
			return res
		return Buffer()
