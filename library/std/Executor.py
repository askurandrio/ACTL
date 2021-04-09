from itertools import zip_longest
from actl import opcodes
from std.objects import Function
from actl.objects import While, Bool, If, AToPy, Object


class Executor:
	HANDLERS = {}

	def __init__(self, code, scope):
		self.scope = scope
		self.stack = []
		self.frames = [iter(code)]

	def execute(self):
		while self.frames:
			try:
				opcode = next(self.frames[-1])
			except StopIteration:
				self.frames.pop(-1)
				continue
				
			if isinstance(opcode, _Frame):
				self.frames.append(opcode)
				continue

			self._executeOpcode(opcode)

	def _executeOpcode(self, opcode):
		try:
			handler = self.HANDLERS[type(opcode)]
		except KeyError as ex:
			raise KeyError(f'Handler for "{opcode}" not found') from ex

		res = handler(self, opcode)
		if isinstance(res, _Frame):
			self.frames.append(iter(res))

	@classmethod
	def addHandler(cls, opcode):
		def decorator(handler):
			cls.HANDLERS[opcode] = handler
		return decorator


class _Frame:
	def __init__(self, head):
		self._head = iter(head)

	def __iter__(self):
		return self

	def __next__(self):
		return next(self._head)

	@classmethod
	def wrap(cls, func):
		def wrapper(*args, **kwargs):
			return cls(func(*args, **kwargs))

		return wrapper


class _CallFrame(_Frame):
	def __init__(self, executor, opcode):
		function = executor.scope[opcode.function]
		executor.scope, self.prevScope = executor.scope.child(), executor.scope

		for functionArg, opcodeArg in zip_longest(
			function.getAttribute('signature').getAttribute('args'), opcode.args
		):
			executor.scope[functionArg] = self.prevScope[opcodeArg]

		self.dst = opcode.dst
		super().__init__(function.getAttribute('body'))


@Executor.addHandler(type(Object))
def _(executor, opcode):
	def getHandler():
		for parent in [
			opcode.getAttribute('__class__'),
			*opcode.getAttribute('__class__').getAttribute('__parents__')
		]:
			if parent in Executor.HANDLERS:
				return Executor.HANDLERS[parent]

		raise RuntimeError(f'Handler for {opcode} not found')

	return getHandler()(executor, opcode)


@Executor.addHandler(opcodes.VARIABLE)
def _(executor, opcode):
	executor.scope['_'] = executor.scope[opcode.name]


@Executor.addHandler(opcodes.SET_VARIABLE)
def _(executor, opcode):
	if opcode.srcStatic is not None:
		src = opcode.srcStatic
	else:
		src = executor.scope[opcode.src]

	executor.scope[opcode.dst] = src


@Executor.addHandler(opcodes.CALL_FUNCTION_STATIC)
def _(executor, opcode):
	assert opcode.typeb == '('
	executor.scope[opcode.dst] = opcode.function(*opcode.args, **opcode.kwargs)


@Executor.addHandler(opcodes.CALL_FUNCTION)
def _ExecutorHandler_callFunction(executor, opcode):
	function = executor.scope[opcode.function]

	if Function == function.getAttribute('__class__'):
		return _CallFrame(executor, opcode)

	assert opcode.typeb == '('
	args = [executor.scope[varName] for varName in opcode.args]
	kwargs = {argName: executor.scope[varName] for argName, varName in opcode.kwargs.items()}
	executor.scope[opcode.dst] = function.call(*args, **kwargs)
	return None


@Executor.addHandler(opcodes.RETURN)
def _(executor, opcode):
	while not isinstance(executor.frames[-1], _CallFrame):
		executor.frames.pop(-1)

	callFrame = executor.frames.pop(-1)
	callFrame.prevScope[callFrame.dst] = executor.scope[opcode.var]		
	executor.scope = callFrame.prevScope


@Executor.addHandler(opcodes.CALL_OPERATOR)
def _(executor, opcode):
	first = executor.scope[opcode.first]
	second = executor.scope[opcode.second]

	assert opcode.operator == '.'
	executor.scope[opcode.dst] = first.getAttribute(str(AToPy(second)))


@Executor.addHandler(While)
@_Frame.wrap
def _(executor, opcode):
	while True:
		yield _Frame(opcode.getAttribute('conditionFrame'))
		res = Bool.call(executor.scope['_'])
		if not AToPy(res):
			break

		yield _Frame(opcode.getAttribute('code'))


@Executor.addHandler(Function)
def _executeFunction(executor, opcode):
	linkedFunction = Function.call(
		opcode.getAttribute('name'),
		opcode.getAttribute('signature'),
		opcode.getAttribute('body'),
		executor.scope
	)
	executor.scope[opcode.getAttribute('name')] = linkedFunction


@Executor.addHandler(If)
@_Frame.wrap
def _(executor, opcode):
	for conditionFrame, code in opcode.getAttribute('conditions'):
		yield _Frame(conditionFrame)
		res = executor.scope['_']
		res = Bool.call(res)
		if AToPy(res):
			yield _Frame(code)
			return

	if opcode.hasAttribute('elseCode'):
		yield _Frame(opcode.getAttribute('elseCode'))
