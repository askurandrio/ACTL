from actl.Buffer import TransactionBuffer, Buffer
from actl.syntax.Template import Template
from actl.utils import loadCoroutine


_nothing = object()


class BufferRule:
	def __init__(self, parser, buff):
		self._parser = parser
		self._buff = buff

	def parseUntil(self, until):
		definition, _ = loadCoroutine(
			self._parser.subParser(self._buff, until).parseUntilLineEnd()
		)
		self._buff.insert(0, definition)

	async def get(self, *template):
		template = Template(*template)
		transactionBuff = TransactionBuffer(self._buff)
		return await template(self._parser, transactionBuff)

	async def pop(self, *template, default=_nothing):
		template = Template(*template)
		buff = await template(self._parser, self._buff)
		if buff is None:
			if default is _nothing:
				raise IndexError(f'{self}.pop({template}) is None')
			buff = default
		return buff

	async def popUntil(self, *template):
		while self._buff and (not await self.startsWith(*template)):
			yield self._buff.pop()

	def __iter__(self):
		return iter(self._buff)

	async def index(self, *template):
		template = Template(*template)
		index = 0
		transactionBuff = TransactionBuffer(self._buff)

		while transactionBuff:
			res = await template(self._parser, transactionBuff)
			if res is not None:
				return index

			index += 1
			del transactionBuff[0]

		raise IndexError(f'Can not find this: {template}')

	async def startsWith(self, *template):
		template = Template(*template)
		transactionBuff = TransactionBuffer(self._buff)

		res = await template(self._parser, transactionBuff)
		return res is not None

	async def contains(self, rule):
		try:
			await self.index(rule)
		except IndexError:
			return False
		return True

	def __str__(self):
		return f'{type(self).__name__}(parser={self._parser}, buff={self._buff})'
