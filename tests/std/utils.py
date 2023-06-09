from actl import Project, Buffer


class AbstractExecute:
	_PROJECT_NAME = None

	def __init__(self):
		self.isParsed = False
		self.isExecuted = False
		self.project = Project()
		self.project.processSource([{'include': self._PROJECT_NAME}])

		# for heat up project
		self.project['initialScope']  # pylint: disable=pointless-statement

		self.executor = None

	def flush(self):
		assert self.executed
		self.isParsed = False
		self.isExecuted = False
		buildScope = self.scope
		self.project = Project()
		self.project.processSource([{'include': self._PROJECT_NAME}])
		self.project['buildScope'] = buildScope

	@property
	def scope(self):
		return self.project['buildScope']

	@property
	def initialScope(self):
		return self.project['initialScope']

	@property
	def code(self):
		return self.project['buildCode']

	@property
	def parsed(self):
		if self.isParsed:
			return self

		self.project['buildCode'] = Buffer(self.project['buildCode'])
		self.isParsed = True
		return self.parsed

	@property
	def executed(self):
		if self.isExecuted:
			return self

		self.project['buildExecutor'].execute(self.project['buildCode'])
		self.isExecuted = True
		return self.executed

	def __call__(self, code):
		buildCode = self.project['parseInput'](self.scope, Buffer(code))
		self.project['buildCode'] = buildCode
