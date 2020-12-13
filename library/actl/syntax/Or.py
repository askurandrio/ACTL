from actl.Buffer import LTransactionBuffer
from actl.syntax.Template import Template
from actl.syntax.AbstractTemplate import AbstractTemplate


class Or(AbstractTemplate):
	__slots__ = ('templates',)

	def __init__(self, *templates):
		templates = tuple(Template(*template) for template in templates)
		super().__init__(templates)

	def __call__(self, parser, inp):
		for template in self.templates:
			lTxInp = LTransactionBuffer(inp)
			res = template(parser, lTxInp)
			if res is not None:
				lTxInp.commit()
				return res

		return None
