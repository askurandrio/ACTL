from actl import opcodes, objects
from actl.objects import While, Bool, If, Function, AToPy, Object


class Executor:
	HANDLERS = {}

	def __init__(self, code, scope):
		self.scope = scope
		self.stack = []
		self.frames = [iter(code)]
		self.execute()

	def execute(self):
		while self.frames:
			try:
				opcode = next(self.frames[-1])
			except StopIteration:
				self.frames.pop(-1)
				continue

			if isinstance(opcode, _Frame):
				self.frames.append(iter(opcode))
				continue

			try:
				handler = self.HANDLERS[type(opcode)]
			except KeyError:
				raise KeyError(f'Handler for "{opcode}" not found')

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
	parents = list(opcode.getAttr('__class__').getAttr('__parents__'))
	while parents[0] not in Executor.HANDLERS:
		parents.pop(0)

	handler = Executor.HANDLERS[parents[0]]
	return handler(executor, opcode)


@Executor.addHandler(opcodes.VARIABLE)
def _(executor, opcode):
	executor.scope['_'] = executor.scope[opcode.name]


@Executor.addHandler(opcodes.SET_VARIABLE)
def _(executor, opcode):
	executor.scope[opcode.dst] = executor.scope[opcode.src]


@Executor.addHandler(opcodes.CALL_FUNCTION_STATIC)
def _(executor, opcode):
	assert opcode.typeb == '('
	executor.scope[opcode.dst] = opcode.function(*opcode.args, **opcode.kwargs)


@Executor.addHandler(opcodes.CALL_FUNCTION)
def _(executor, opcode):
	function = executor.scope[opcode.function]
	if Function in function.getAttr('__class__').getAttr('__parents__'):
		return _executeFunction(executor, opcode)

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


@Executor.addHandler(opcodes.CALL_OPERATOR)
def _(executor, opcode):
	first = executor.scope[opcode.first]
	second = executor.scope[opcode.second]

	assert opcode.operator == '.'
	executor.scope[opcode.dst] = first.getAttr(str(AToPy(second)))


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


def _executeFunction(executor, opcode):
	function = executor.scope[opcode.function]
	executor.stack.append(_CallFrame(executor.frames, opcode.dst))
	executor.frames = [iter(function.getAttr('body'))]
