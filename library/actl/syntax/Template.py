# pylint: disable=no-member
from actl.Buffer import TransactionBuffer, Buffer
from actl.syntax.AbstractTemplate import AbstractTemplate


class _MetaTemplate(type(AbstractTemplate)):
	def __call__(self, *args):
		if (len(args) == 1) and isinstance(args[0], Template):
			return args[0]
		return super().__call__(*args)


class Template(AbstractTemplate, metaclass=_MetaTemplate):
	__slots__ = ('_template',)

	def __init__(self, *template):
		super().__init__(template)

	async def __call__(self, parser, buff):
		transactionBuff = TransactionBuffer(buff)
		res = Buffer()

		for tmpl in self._template:
			if tmpl is breakpoint:
				tmpl()
				continue

			tmplRes = await tmpl(parser, transactionBuff)
			if tmplRes is None:
				return None
			try:
				res += tmplRes
			except:
				print(self, tmpl)
				raise

		transactionBuff.commit()
		return res

	def __repr__(self):
		reprTemplate = ', '.join(str(tmpl) for tmpl in self._template)
		return f'{type(self).__name__}({reprTemplate})'
