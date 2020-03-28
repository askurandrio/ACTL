from actl.utils import SlotsViaGetAttr
from actl.syntax.Template import Template


class BufferRule(SlotsViaGetAttr):
	def __init__(self, parser, buff):
		self._parser = parser
		self._buff = buff

	def get(self, *template):
		template = Template(*template)

		with self._buff.transaction():
			return template(self._parser, self._buff)

	def pop(self, *template):
		template = Template(*template)
		buff = template(self._parser, self._buff)
		if buff is None:
			raise IndexError(f'{self}.pop({template}) is None')
		return buff

	def popUntil(self, *template):
		res = type(self._buff)()
		while self._buff and (not self.startsWith(*template)):
			res.append(self._buff.pop())
		return res

	def index(self, *template):
		template = Template(*template)
		index = 0
		with self._buff.transaction():
			while self._buff:
				res = template(self._parser, self._buff)
				if res is not None:
					return index

				index += 1
				self._buff.pop()

		raise IndexError(f'Can not find this: {template}')

	def startsWith(self, *template):
		template = Template(*template)

		with self.transaction():
			res = template(self._parser, self._buff)
			return res is not None

	def __contains__(self, rule):
		try:
			self.index(rule)
		except IndexError:
			return False
		return True

	def __getattr__(self, key):
		return getattr(self._buff, key)

	def __str__(self):
		return f'{type(self).__name__}(parser={self._parser}, buff={self._buff})'
