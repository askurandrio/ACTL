from actl.Buffer import LTransactionBuffer, Buffer
from actl.syntax.Template import Template


class BufferRule:
	def __init__(self, parser, buff):
		self._parser = parser
		self._buff = buff

	def parseUntil(self, until):
		self._parser.subParser(self._buff, until).parseLine()

	def get(self, *template):
		template = Template(*template)
		lTxBuff = LTransactionBuffer(self._buff)
		return template(self._parser, lTxBuff)

	def popOrNone(self, *template):
		template = Template(*template)
		return template(self._parser, self._buff)

	def pop(self, *template):
		buff = self.popOrNone(*template)
		if buff is None:
			raise IndexError(f'{self}.pop({template}) is None')
		return buff

	def popUntil(self, *template):
		res = Buffer()
		while self._buff and (not self.startsWith(*template)):
			res.append(self._buff.pop())
		return res

	def index(self, *template):
		template = Template(*template)
		index = 0
		lTxBuff = LTransactionBuffer(self._buff)

		while lTxBuff:
			res = template(self._parser, lTxBuff)
			if res is not None:
				return index

			index += 1
			lTxBuff.pop()

		raise IndexError(f'Can not find this: {template}')

	def startsWith(self, *template):
		template = Template(*template)
		lTxBuff = LTransactionBuffer(self._buff)

		res = template(self._parser, lTxBuff)
		return res is not None

	def __contains__(self, rule):
		try:
			self.index(rule)
		except IndexError:
			return False
		return True

	def __str__(self):
		return f'{type(self).__name__}(parser={self._parser}, buff={self._buff})'
