from actl import opcodes, ResultReturnException
from actl.objects import While, Bool, If, AToPy, Object, class_ as actlClass
from std.objects import Function, class_ as stdClass


class Executor:
	HANDLERS = {}

	def __init__(self, code, scope):
		self.scope = scope
		self.stack = []
		self.frames = [iter(code)]
		self.returnHandler = None

	def execute(self):
		while self.frames:
			try:
				opcode = next(self.frames[-1])
			except StopIteration:
				self.frames.pop(-1)
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


class _ResultFrame(_Frame):
	def __init__(self, executor, result):
		self._executor = executor
		self._finalResult = result
		self._result = result.getParent()
		super().__init__(self._result.popExecute(self._executor))

	def return_(self, returnValue):
		try:
			self._head.throw(ResultReturnException(returnValue))
		except ResultReturnException:
			pass
		else:
			raise RuntimeError(f'This generator do not want return: {self._head}')

		self._result = self._result.resolve(returnValue)
		if self._result is None:
			self._head = None
			assert self._executor.frames.pop(-1) == self
		else:
			self._head = self._result.popExecute(self._executor)

	def __next__(self):
		if self._head is None:
			raise StopIteration

		try:
			return super().__next__()
		except StopIteration as ex:
			raise RuntimeError('Unexpected end of code') from ex


@Executor.addHandler(type(Object))
def _(executor, opcode):
	def getHandler():
		class_ = opcode.getAttribute.obj('__class__').obj
		for parent in [
			class_,
			*class_.getAttribute.obj('__parents__').obj
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
	result = opcode.function(*opcode.args, **opcode.kwargs)
	executor.scope[opcode.dst] = result.obj


@Executor.addHandler(opcodes.CALL_FUNCTION)
def _ExecutorHandler_callFunction(executor, opcode):
	function = executor.scope[opcode.function]

	assert opcode.typeb == '('
	args = [executor.scope[varName] for varName in opcode.args]
	kwargs = {argName: executor.scope[varName] for argName, varName in opcode.kwargs.items()}

	resultCall = function.call.obj(*args, **kwargs)

	@resultCall.then
	def setDstForResultCall(returnValue):
		executor.scope[opcode.dst] = returnValue

	if setDstForResultCall.isResolved():
		return

	return _ResultFrame(executor, setDstForResultCall)


@Executor.addHandler(opcodes.RETURN)
def _(executor, opcode):
	returnVal = executor.scope[opcode.var]

	while not isinstance(executor.frames[-1], _ResultFrame):
		del executor.frames[-1]

	executor.frames[-1].return_(returnVal)


@Executor.addHandler(opcodes.CALL_OPERATOR)
def _(executor, opcode):
	first = executor.scope[opcode.first]
	second = executor.scope[opcode.second]

	assert opcode.operator == '.'
	executor.scope[opcode.dst] = first.getAttribute.obj(str(AToPy(second))).obj


@Executor.addHandler(While)
@_Frame.wrap
def _(executor, opcode):
	while True:
		yield from opcode.getAttribute.obj('conditionFrame').obj
		res = Bool.call.obj(executor.scope['_']).obj
		if not AToPy(res):
			break

		yield from opcode.getAttribute.obj('code').obj


@Executor.addHandler(Function)
def _executeFunction(executor, opcode):
	linkedFunction = Function.call.obj(
		opcode.getAttribute.obj('name').obj,
		opcode.getAttribute.obj('signature').obj,
		opcode.getAttribute.obj('body').obj,
		executor.scope
	).obj
	executor.scope[opcode.getAttribute.obj('name').obj] = linkedFunction


@Executor.addHandler(If)
@_Frame.wrap
def _(executor, opcode):
	for conditionFrame, code in opcode.getAttribute.obj('conditions').obj:
		yield from conditionFrame
		res = executor.scope['_']
		res = Bool.call.obj(res).obj
		if AToPy(res):
			yield from code
			return

	if opcode.hasAttribute('elseCode'):
		yield from opcode.getAttribute.obj('elseCode').obj


@Executor.addHandler(actlClass)
@_Frame.wrap
def _executeClass(executor, opcode):
	className = str(opcode.getAttribute.obj('__name__').obj)
	newClass = stdClass.call.obj(className, {}).obj
	executor.scope, prevScope = executor.scope.child(), executor.scope
	executor.scope['__class__'] = newClass
	executor.scope[className] = newClass
	self_ = newClass.getAttribute.obj('__self__').obj

	yield from opcode.getAttribute.obj('body').obj

	for key, value in executor.scope.getDiff():
		if key in ['__class__', className, '__name__']:
			continue

		if Function == value.getAttribute.obj('__class__').obj:
			self_[key] = value
			continue

		newClass.setAttribute(key, value)

	executor.scope = prevScope
	executor.scope[className] = newClass
