from actl import opcodes
from actl.objects import While, Bool, If, AToPy, Object, class_ as actlClass
from std.base.objects import Function, class_ as stdClass


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
		except KeyError:
			error = KeyError(f'Opcode<"{opcode}"> is not expected')
			self.frames[-1].throw(error)

		try:
			res = handler(self, opcode)
		except Exception as ex:
			self.frames[-1].throw(ex)

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

	def throw(self, error):
		self._head.throw(error)

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
		super().__init__(self._result.getExecute()(self._executor))

	def return_(self, returnValue):
		self._head.close()

		self._result = self._result.resolve(returnValue)
		if self._result is None:
			self._head = iter('')
			assert self._executor.frames.pop(-1) == self
		else:
			self._head = self._result.getExecute()(self._executor)

	def __next__(self):
		try:
			return super().__next__()
		except StopIteration:
			assert self._result is None
			raise

	@classmethod
	def wrap(cls, executor, result):
		if result.isResolved():
			return

		return cls(executor, result)


@Executor.addHandler(type(Object))
def _(executor, opcode):
	def getHandler():
		class_ = opcode.getAttribute('__class__').obj
		for parent in [
			class_,
			*class_.getAttribute('__parents__').obj
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
	src = executor.scope[opcode.src]

	executor.scope[opcode.dst] = src


@Executor.addHandler(opcodes.CALL_FUNCTION_STATIC)
def _(executor, opcode):
	assert opcode.typeb == '('
	resultCall = opcode.function(*opcode.args, **opcode.kwargs)

	@resultCall.then
	def setDstForResultCall(returnValue):
		executor.scope[opcode.dst] = returnValue

	return _ResultFrame.wrap(executor, setDstForResultCall)


@Executor.addHandler(opcodes.CALL_FUNCTION)
def _ExecutorHandler_callFunction(executor, opcode):
	function = executor.scope[opcode.function]

	assert opcode.typeb == '('
	args = [executor.scope[varName] for varName in opcode.args]
	kwargs = {argName: executor.scope[varName] for argName, varName in opcode.kwargs.items()}

	resultCall = function.call(*args, **kwargs)

	@resultCall.then
	def setDstForResultCall(returnValue):
		executor.scope[opcode.dst] = returnValue

	return _ResultFrame.wrap(executor, setDstForResultCall)


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
	assert opcode.operator == '+'

	pyFirst = AToPy(first)
	pySecond = AToPy(second)
	pyResult = pyFirst + pySecond

	resultClass = first.getAttribute('__class__').obj
	result = resultClass.call(pyResult).obj

	executor.scope[opcode.dst] = result


@Executor.addHandler(opcodes.GET_ATTRIBUTE)
def _(executor, opcode):
	object_ = executor.scope[opcode.object]
	attribute = opcode.attribute

	executor.scope[opcode.dst] = object_.getAttribute(attribute).obj


@Executor.addHandler(opcodes.SET_ATTRIBUTE)
def _(executor, opcode):
	object_ = executor.scope[opcode.object]
	attribute = opcode.attribute
	src = executor.scope[opcode.src]

	object_.setAttribute(attribute, src)


@Executor.addHandler(While)
@_Frame.wrap
def _(executor, opcode):
	while True:
		yield from opcode.getAttribute('conditionFrame').obj
		res = Bool.call(executor.scope['_']).obj
		if not AToPy(res):
			break

		yield from opcode.getAttribute('code').obj


@Executor.addHandler(Function)
def _executeFunction(executor, opcode):
	linkedFunction = Function.call(
		opcode.getAttribute('name').obj,
		opcode.getAttribute('signature').obj,
		opcode.getAttribute('body').obj,
		executor.scope
	).obj
	executor.scope[opcode.getAttribute('name').obj] = linkedFunction


@Executor.addHandler(If)
@_Frame.wrap
def _(executor, opcode):
	for conditionFrame, code in opcode.getAttribute('conditions').obj:
		yield from conditionFrame
		res = executor.scope['_']
		res = Bool.call(res).obj
		if AToPy(res):
			yield from code
			return

	if opcode.hasAttribute('elseCode'):
		yield from opcode.getAttribute('elseCode').obj


@Executor.addHandler(actlClass)
@_Frame.wrap
def _executeClass(executor, opcode):
	className = str(opcode.getAttribute('__name__').obj)
	newClass = stdClass.call(className, {}).obj
	executor.scope, prevScope = executor.scope.child(), executor.scope
	executor.scope['__class__'] = newClass
	executor.scope[className] = newClass
	self_ = newClass.getAttribute('__self__').obj

	yield from opcode.getAttribute('body').obj

	for key, value in executor.scope.getDiff():
		if key in ['__class__', className, '__name__']:
			continue

		if Function == value.getAttribute('__class__').obj:
			self_[key] = value
			continue

		newClass.setAttribute(key, value)

	executor.scope = prevScope
	executor.scope[className] = newClass
