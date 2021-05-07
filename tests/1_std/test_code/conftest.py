import pytest

from actl.Buffer import Buffer
from actl import Project


@pytest.fixture
def execute():
	return _Execute()


class _Execute:
	def __init__(self):
		self.isParsed = False
		self.isExecuted = False
		self._project = Project('std/base')


	def flush(self):
		self.isParsed = False
		self.isExecuted = False
		buildScope = self.scope
		self._project = Project('std/base')
		self._project['initialScope'] = buildScope

	@property
	def scope(self):
		return self._project['buildScope']

	@property
	def code(self):
		return self._project['buildParser']

	@property
	def parsed(self):
		if self.isParsed:
			return self

		self._project['buildParser'] = Buffer(self._project['buildParser'])
		self.isParsed = True
		return self.parsed

	@property
	def executed(self):
		if self.isExecuted:
			return self

		self._project.this['buildExecutor'].execute()
		self.isExecuted = True
		return self.executed

	def __call__(self, code):
		self._project['input'] = Buffer(code)
