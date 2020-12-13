# pylint: disable=no-member
from actl.Buffer import LTransactionBuffer, Buffer
from actl.syntax.AbstractTemplate import AbstractTemplate


class _MetaTemplate(type(AbstractTemplate)):
	def __call__(self, *template):
		if (len(template) == 1) and isinstance(template[0], AbstractTemplate):
			return template[0]
		return super().__call__(*template)


class Template(AbstractTemplate, metaclass=_MetaTemplate):
	__slots__ = ('_template',)

	def __init__(self, *template):
		super().__init__(template)

	def __call__(self, parser, buff):
		lTxBuff = LTransactionBuffer(buff)
		res = Buffer()

		for tmpl in self._template:
			tmplRes = tmpl(parser, lTxBuff)
			if tmplRes is None:
				return None
			res += tmplRes

		lTxBuff.commit()
		return res

	def __repr__(self):
		reprTemplate = ', '.join(str(tmpl) for tmpl in self._template)
		return f'{type(self).__name__}({reprTemplate})'
