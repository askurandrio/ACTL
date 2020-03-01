from actl import opcodes
from actl.objects import While, Object, Bool, If, Function, AToPy


class Executor:
	HANDLERS = {}

	def __init__(self, code, scope):
		self.scope = scope
		self.stack = []
		self.frames = [iter(code)]
		self._execute()

	def _execute(self):
		while self.frames:
			try:
				opcode = next(self.frames[-1])
			except StopIteration:
				self.frames.pop(-1)
				continue

			if isinstance(opcode, _Frame):
				self.frames.append(iter(opcode))
				continue

			handler = self.HANDLERS[type(opcode)]
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
		self._head = head

	def __iter__(self):
		yield from self._head

	@classmethod
	def wrap(cls, func):
		def wrapper(*args, **kwargs):
			return cls(func(*args, **kwargs))

		return wrapper


class _CallFrame:
	def __init__(self, frames, returnVar):
		self.frames = frames
		self.returnVar = returnVar


@Executor.addHandler(type(Object))
def _(executor, opcode):
	handler = Executor.HANDLERS[opcode.getAttr('__class__')]
	return handler(executor, opcode)


@Executor.addHandler(opcodes.VARIABLE)
def _(executor, opcode):
	executor.scope['_'] = executor.scope[opcode.name]


@Executor.addHandler(opcodes.SET_VARIABLE)
def _(executor, opcode):
	if opcode.val is not None:
		val = opcode.val
	elif opcode.src is not None:
		val = executor.scope[opcode.src]
	executor.scope[opcode.dst] = val


@Executor.addHandler(opcodes.CALL_FUNCTION_STATIC)
def _(executor, opcode):
	function = executor.scope[opcode.function]
	assert opcode.typeb == '('
	executor.scope[opcode.dst] = function.call(*opcode.args, **opcode.kwargs)


@Executor.addHandler(opcodes.CALL_FUNCTION)
def _(executor, opcode):
	function = executor.scope[opcode.function]
	if function.getAttr('__class__') is Function:
		return Executor.HANDLERS[Function](executor, opcode)

	assert opcode.typeb == '('
	args = (executor.scope[key] for key in opcode.args)
	kwargs = {key: executor.scope[key] for key in opcode.kwargs}
	executor.scope[opcode.dst] = function.call(*args, **kwargs)
	return None


@Executor.addHandler(opcodes.RETURN)
def _(executor, opcode):
	callFrame = executor.stack.pop(-1)
	executor.frames = callFrame.frames
	executor.scope[callFrame.returnVar] = executor.scope[opcode.var]


@Executor.addHandler(While)
@_Frame.wrap
def _(executor, opcode):
	while True:
		yield _Frame(opcode.getAttr('conditionFrame'))
		res = Bool.call(executor.scope['_'])
		if not AToPy(res):
			break

		yield _Frame(opcode.getAttr('code'))


@Executor.addHandler(If)
@_Frame.wrap
def _(executor, opcode):
	for conditionFrame, code in opcode.getAttr('conditions'):
		yield _Frame(conditionFrame)
		res = executor.scope['_']
		res = Bool.call(res)
		if AToPy(res):
			yield _Frame(code)
			return

	if opcode.hasAttr('elseCode'):
		yield _Frame(opcode.getAttr('elseCode'))


@Executor.addHandler(Function)
def _(executor, opcode):
	function = executor.scope[opcode.function]
	executor.stack.append(_CallFrame(executor.frames, opcode.dst))
	executor.frames = [iter(function.getAttr('body'))]
