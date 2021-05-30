from actl import opcodes
from actl.objects import While, Bool, If, AToPy, Object, class_ as actlClass, Result
from std.base.objects import Function, class_ as stdClass


class Executor:
	_HANDLERS = {}

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
			handler = self.getHandlerFor(type(opcode))
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
	def wrap(cls, executor, dst, result):
		if not isinstance(result, Result):
			executor.scope[dst] = result
			return

		@result.then
		def storeResult(res):
			executor.scope[dst] = res

		return cls(executor, storeResult)


@Executor.addHandler(type(Object))
def _objectHandler(executor, opcode):
	def getHandler():
		class_ = opcode.getAttribute('__class__')
		for parent in [
			class_,
			*class_.getAttribute('__parents__')
		]:
			try:
				return executor.getHandlerFor(parent)
			except KeyError:
				pass

		raise RuntimeError(f'Handler for {opcode} not found')

	return getHandler()(executor, opcode)


@Executor.addHandler(opcodes.VARIABLE)
def _VARIABLE__handler(executor, opcode):
	pass


@Executor.addHandler(opcodes.SET_VARIABLE)
def _SET_VARIABLE__handler(executor, opcode):
	src = executor.scope[opcode.src]

	executor.scope[opcode.dst] = src


@Executor.addHandler(opcodes.CALL_FUNCTION_STATIC)
def _CALL_FUNCTION_STATIC__handler(executor, opcode):
	assert opcode.typeb == '('

	result = opcode.function(*opcode.args, **opcode.kwargs)

	return _ResultFrame.wrap(executor, opcode.dst, result)


@Executor.addHandler(opcodes.CALL_FUNCTION)
def _CALL_FUNCTION__handler(executor, opcode):
	function = executor.scope[opcode.function]

	assert opcode.typeb == '('
	args = [executor.scope[varName] for varName in opcode.args]
	kwargs = {argName: executor.scope[varName] for argName, varName in opcode.kwargs.items()}

	result = function.call(*args, **kwargs)


	return _ResultFrame.wrap(executor, opcode.dst, result)


@Executor.addHandler(opcodes.RETURN)
def _RETURN__handler(executor, opcode):
	returnVal = executor.scope[opcode.var]

	while not isinstance(executor.frames[-1], _ResultFrame):
		del executor.frames[-1]

	executor.frames[-1].return_(returnVal)


@Executor.addHandler(opcodes.CALL_OPERATOR)
def _CALL_OPERATOR__handler(executor, opcode):
	first = executor.scope[opcode.first]
	second = executor.scope[opcode.second]
	assert opcode.operator == '+'

	pyFirst = AToPy(first)
	pySecond = AToPy(second)
	pyResult = pyFirst + pySecond

	resultClass = first.getAttribute('__class__')
	result = resultClass.call(pyResult)

	executor.scope[opcode.dst] = result


@Executor.addHandler(opcodes.GET_ATTRIBUTE)
def _GET_ATTRIBUTE__handler(executor, opcode):
	object_ = executor.scope[opcode.object]
	attribute = opcode.attribute

	executor.scope[opcode.dst] = object_.getAttribute(attribute)


@Executor.addHandler(opcodes.SET_ATTRIBUTE)
def _SET_ATTRIBUTE__handler(executor, opcode):
	object_ = executor.scope[opcode.object]
	attribute = opcode.attribute
	src = executor.scope[opcode.src]

	object_.setAttribute(attribute, src)


@Executor.addHandler(While)
@_Frame.wrap
def _While__handler(executor, opcode):
	while True:
		yield from opcode.getAttribute('conditionFrame')
		res = Bool.call(executor.scope[opcode.getAttribute('conditionFrame')[-1].name])
		if not AToPy(res):
			break

		yield from opcode.getAttribute('code')


@Executor.addHandler(Function)
def _Function__handler(executor, opcode):
	linkedFunction = Function.call(
		opcode.getAttribute('name'),
		opcode.getAttribute('signature'),
		opcode.getAttribute('body'),
		executor.scope
	)
	executor.scope[opcode.getAttribute('name')] = linkedFunction


@Executor.addHandler(If)
@_Frame.wrap
def _If__handler(executor, opcode):
	for conditionFrame, code in opcode.getAttribute('conditions'):
		yield from conditionFrame
		res = executor.scope[conditionFrame[-1].name]
		res = Bool.call(res)
		if AToPy(res):
			yield from code
			return

	if opcode.hasAttribute('elseCode'):
		yield from opcode.getAttribute('elseCode')


@Executor.addHandler(actlClass)
@_Frame.wrap
def _actlClass__handler(executor, opcode):
	className = str(opcode.getAttribute('__name__'))
	newClass = stdClass.call(className, {})
	executor.scope, prevScope = executor.scope.child(), executor.scope
	executor.scope['__class__'] = newClass
	executor.scope[className] = newClass
	self_ = newClass.getAttribute('__self__')

	yield from opcode.getAttribute('body')

	for key, value in executor.scope.getDiff():
		if key in ['__class__', className, '__name__']:
			continue

		if Function == value.getAttribute('__class__'):
			self_[key] = value
			continue

		newClass.setAttribute(key, value)

	executor.scope = prevScope
	executor.scope[className] = newClass
