from actl.Buffer import TransactionBuffer, Buffer
from actl.syntax.Template import Template


_nothing = object()


class BufferRule:
	def __init__(self, parser, buff):
		self._parser = parser
		self._buff = buff

	def parseUntil(self, until):
		self._parser.subParser(self._buff, until).parseUntilLineEnd()

	def get(self, *template):
		template = Template(*template)
		transactionBuff = TransactionBuffer(self._buff)
		return template(self._parser, transactionBuff)

	def pop(self, *template, default=_nothing):
		template = Template(*template)
		buff = template(self._parser, self._buff)
		if buff is None:
			if default is _nothing:
				raise IndexError(f'{self}.pop({template}) is None')
			buff = default
		return buff

	@Buffer.wrap
	def popUntil(self, *template):
		while self._buff and (not self.startsWith(*template)):
			yield self._buff.pop()

	def __iter__(self):
		return iter(self._buff)

	def index(self, *template):
		template = Template(*template)
		index = 0
		transactionBuff = TransactionBuffer(self._buff)

		while transactionBuff:
			res = template(self._parser, transactionBuff)
			if res is not None:
				return index

			index += 1
			del transactionBuff[0]

		raise IndexError(f'Can not find this: {template}')

	def startsWith(self, *template):
		template = Template(*template)
		transactionBuff = TransactionBuffer(self._buff)

		res = template(self._parser, transactionBuff)
		return res is not None

	def __contains__(self, rule):
		try:
			self.index(rule)
		except IndexError:
			return False
		return True

	def __str__(self):
		return f'{type(self).__name__}(parser={self._parser}, buff={self._buff})'
