class Executor:
	_HANDLERS = {}

	def __init__(self, scope):
		self.scope = scope
		self.callStack = []
		self.setReturnValue = None
		self.frames = []

	def executeCoroutine(self, coroutine):
		from std.base.executor.utils import makeCoroutineResultSaver

		result = None

		@makeCoroutineResultSaver(coroutine)
		def saveCoroutineResult(res):
			nonlocal result
			result = res

		self.execute(saveCoroutineResult.__await__())

		return result

	def execute(self, code):
		previusCallStack, previusSetReturnValue, previusFrames = (
			self.callStack,
			self.setReturnValue,
			self.frames,
		)
		self.callStack, self.setReturnValue, self.frames = [], None, [iter(code)]

		while self.frames:
			try:
				opcode = next(self.frames[-1])
			except StopIteration:
				self.frames.pop(-1)
				continue

			self._executeOpcode(opcode)

		self.callStack, self.setReturnValue, self.frames = (
			previusCallStack,
			previusSetReturnValue,
			previusFrames,
		)

	def _executeOpcode(self, opcode):
		try:
			handler = self.getHandlerFor(type(opcode))
		except KeyError as ex:
			raise KeyError(f'Opcode<"{opcode}"> is not expected') from ex

		coroutine = handler(self, opcode)
		self.frames.append(coroutine.__await__())

	@classmethod
	def addHandler(cls, opcode):
		def decorator(handler):
			cls._HANDLERS[opcode] = handler

		return decorator

	@classmethod
	def getHandlerFor(cls, opcodeType):
		for parent in cls.__mro__:
			if not hasattr(parent, '_HANDLERS'):
				continue

			try:
				return parent._HANDLERS[opcodeType]
			except KeyError:
				pass

		raise KeyError(f'opcodeType<{opcodeType}> is not expected')
