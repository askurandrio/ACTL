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
		template(self._parser, self._buff)

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
