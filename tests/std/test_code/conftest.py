import pytest

from actl import Buffer, opcodes, Project


@pytest.fixture
def execute():
	return _Execute()


class _Execute:
	def __init__(self):
		opcodes.VARIABLE.counter.reset()

		self.isParsed = False
		self.isExecuted = False
		self._project = Project('std')

	@property
	def scope(self):
		return self._project['scope']

	@property
	def code(self):
		return self._project['code']

	@property
	def parsed(self):
		if self.isParsed:
			return self

		code = self._project['parse']()  # pylint: disable=not-callable
		self._project['code'] = Buffer(code)
		self.isParsed = True
		return self.parsed

	@property
	def executed(self):
		if self.parsed.isExecuted:
			return self

		self._project['execute']()  # pylint: disable=not-callable
		self.isExecuted = True
		return self.executed

	def __call__(self, code):
		self._project['uinput'] = Buffer(code)
