import pytest

from actl.Buffer import Buffer
from actl import Project
from std import Executor


@pytest.fixture
def execute():
	return _Execute()


class _Execute:
	def __init__(self):
		self.isParsed = False
		self.isExecuted = False
		self._project = Project('std')

	def flush(self):
		self.isParsed = False
		self.isExecuted = False
		scope = self.scope
		self._project = Project('std')
		self._project['scope'] = scope

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

		self._project['code'] = Buffer(self._project['parser'])
		self.isParsed = True
		return self.parsed

	@property
	def executed(self):
		if self.parsed.isExecuted:
			return self

		self._project['executor'] = Executor(self._project['code'], self._project['scope'])
		self._project['executor'].execute()
		self.isExecuted = True
		return self.executed

	def __call__(self, code):
		self._project['input'] = Buffer(code)
