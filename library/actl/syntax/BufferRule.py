from actl.Lazy import SlotsViaGetAttr
from actl.syntax.Template import Template


class BufferRule(SlotsViaGetAttr):
	def __init__(self, parser, buff):
		self._parser = parser
		super().__init__(buff)

	def get(self, *template):
		template = Template(*template)

		with self._value.transaction():
			return template(self._parser, self._value)

	def pop(self, *template):
		template = Template(*template)
		template(self._parser, self._value)

	def index(self, *template):
		template = Template(*template)
		index = 0
		with self._value.transaction():
			while self._value:
				res = template(self._parser, self._value)
				if res is not None:
					return index

				index += 1
				self._value.pop()

		raise IndexError(f'Can not find this: {template}')

	def startsWith(self, *template):
		template = Template(*template)

		with self._value.transaction():
			res = template(self._parser, self._value)
			return res is not None

	def __contains__(self, rule):  # pylint: disable=invalid-overridden-method
		try:
			self.index(rule)
		except IndexError:
			return False
		return True
