
import actl
from actl.objects import While, Object, Bool, If, Function, AToPy


class Executor:
	HANDLERS = {}

	def __init__(self, code, scope):
		self.scope = scope
		self._frames = [iter(code)]
		self._execute()

	def _execute(self):
		while self._frames:
			try:
				opcode = next(self._frames[-1])
			except StopIteration:
				self._frames.pop(-1)
				continue

			if isinstance(opcode, _Frame):
				self._frames.append(iter(opcode))
				continue

			handler = self.HANDLERS[type(opcode)]
			res = handler(self, opcode)
			if isinstance(res, _Frame):
				self._frames.append(iter(res))

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


@Executor.addHandler(type(Object))
def _(executor, opcode):
	handler = Executor.HANDLERS[opcode.getAttr('__class__')]
	return handler(executor, opcode)


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


@Executor.addHandler(actl.opcodes.VARIABLE)
def _(executor, opcode):
	executor.scope['_'] = executor.scope[opcode.name]


@Executor.addHandler(actl.opcodes.SET_VARIABLE)
def _(executor, opcode):
	if opcode.val is not None:
		val = opcode.val
	elif opcode.src is not None:
		val = executor.scope[opcode.src]
	executor.scope[opcode.dst] = val


@Executor.addHandler(actl.opcodes.CALL_FUNCTION_STATIC)
def _(executor, opcode):
	function = executor.scope[opcode.function]
	assert opcode.typeb == '('
	executor.scope[opcode.dst] = function.call(*opcode.args, **opcode.kwargs)


@Executor.addHandler(actl.opcodes.CALL_FUNCTION)
@_Frame.wrap
def _(executor, opcode):
	function = executor.scope[opcode.function]
	if function.getAttr('__class__') is Function:
		yield _Frame(function.getAttr('body'))
		executor.scope[opcode.dst] = executor.scope['_']
	else:
		assert opcode.typeb == '('
		args = (executor.scope[key] for key in opcode.args)
		kwargs = {key: executor.scope[key] for key in opcode.kwargs}
		executor.scope[opcode.dst] = function.call(*args, **kwargs)
