import weakref


_default = object()


class Result:
	def __init__(self, obj=_default, ex=_default, execute=_default, _handlers=(), _parent=None):
		if execute is _default:
			if obj is not _default:
				assert not isinstance(obj, Result)
			elif ex is not _default:
				assert not isinstance(ex, Result)
			else:
				assert False
		else:
			assert (obj is _default) and (ex is _default)

		self._obj = obj
		self._ex = ex
		self._execute = execute
		self._handlers = _handlers
		self._parent = _parent
		self._then = None

	def isResolved(self):
		return (self._obj is not _default) or (self._ex is not _default)

	def popExecute(self, executor):
		execute, self._execute = self._execute, _default
		return execute(executor)

	def getParent(self):
		parent = self

		while parent._parent is not None:
			parent = parent._parent

		return parent

	def resolve(self, resolveValue):
		currentResult = self._then

		while currentResult is not None:
			currentResult._parent = None
			handler, _ = currentResult._handlers
			resolveValue = handler(resolveValue)

			if isinstance(resolveValue, Result):
				resolveValue._then = currentResult._then
				currentResult = resolveValue
			else:
				currentResult = currentResult._then

			if (currentResult is not None) and (currentResult._execute is not None):
				return currentResult

		return None

	@property
	def obj(self):
		if self._ex is not _default:
			raise self._ex

		assert self._obj is not _default

		return self._obj

	def then(self, handler, errHandler=None):
		assert self._then is None

		if (self._obj is not _default) and (handler is not None):
			try:
				obj = handler(self._obj)
			except Exception as ex:
				return Result(ex=ex)

			if isinstance(obj, Result):
				return obj

			return Result(obj=obj)

		if self._ex is not _default:
			if errHandler is not None:
				try:
					obj = errHandler(self._ex)
				except Exception as ex:
					return Result(ex=ex)

				if isinstance(obj, Result):
					return obj
			else:
				return Result(ex=self._ex)

		then = Result(
			execute=self._execute, _handlers=(handler, errHandler), _parent=self
		)
		self._then = weakref.proxy(then)
		return then

	def __repr__(self):
		return str(self)

	def __str__(self):
		return f'{type(self).__name__}({self._obj}, {self._ex}, {self._execute})'


class ResultReturnException(Exception):
	def __init__(self, returnValue):
		super().__init__()
		self.returnValue = returnValue
