from actl import Project, Buffer
from std.base.executor.Executor import Executor


class AbstractExecute:
	_PROJECT_NAME = None

	def __init__(self):
		self.isParsed = False
		self.isExecuted = False
		self._project = Project(source=[{'include': self._PROJECT_NAME}])

	def executeInInitialScope(self, code):
		initialScope = self._project['initialScope']
		initialScopeChild = initialScope.child()
		type(initialScopeChild).allowOverride = True

		Executor(
			iter(
				self._project['parseInput'](initialScope, Buffer(code))
			),
			initialScope
		).execute()

		type(initialScopeChild).allowOverride = False

	def flush(self):
		assert self.executed
		self.isParsed = False
		self.isExecuted = False
		buildScope = self.scope
		self._project = Project(source=[{'include': self._PROJECT_NAME}])
		self._project['buildScope'] = buildScope

	@property
	def scope(self):
		return self._project['buildScope']

	@property
	def initialScope(self):
		return self._project['initialScope']

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
		if self.parsed.isExecuted:
			return self

		self._project.this['buildExecutor'].execute()
		self.isExecuted = True
		return self.executed

	def __call__(self, code):
		self._project['input'] = Buffer(code)
