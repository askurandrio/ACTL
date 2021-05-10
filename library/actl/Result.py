import weakref
from actl.utils import default


class Result:
	def __init__(self, obj=default, _handler=None, _parent=None):
		if obj is not default:
			assert _handler is None
		elif _handler is not None:
			assert obj is default
		else:
			assert False

		self._obj = obj
		self._handler = _handler
		self._parent = _parent
		self._child = None

	def isResolved(self):
		_ResultObj.checkEx(self._obj)
		return _ResultObj.isObjAvailable(self._obj)

	def __call__(self, *args, **kwargs):
		@self.then
		def result(obj):
			return obj(*args, **kwargs)

		return result

	def getExecute(self):
		_ResultObj.checkEx(self._obj)
		return _ResultObj.getExecute(self._obj)

	def getParent(self):
		# pylint: disable=protected-access

		result = self

		while result._parent is not None:
			parent = result._parent
			result._parent = None
			parent._child = result
			result = parent

		return result

	def resolve(self, resolveValue):
		# pylint: disable=protected-access
		result = self._child

		while result is not None:
			resolveValue = result._callHandler(resolveValue)

			if not isinstance(resolveValue, Result):
				result = result._child
				continue

			resolveValue._child = result._child
			result = resolveValue.getParent()
			assert not result.isResolved()
			return result

		return None

	def _callHandler(self, resolveValue):
		assert self._handler is not None, self

		if 'then' in self._handler:
			assert 'finally' not in self._handler, self._handler
			return self._handler['then'](resolveValue)

		assert 'then' not in self._handler, self._handler
		return self._handler['finally'](resolveValue, default)

	@property
	def obj(self):
		_ResultObj.checkEx(self._obj)
		return _ResultObj.getObj(self._obj)

	def then(self, handler):
		assert self._child is None

		if _ResultObj.isObjAvailable(self._obj):
			try:
				result = handler(_ResultObj.getObj(self._obj))
			except Exception as ex: # pylint: disable=broad-except
				return Result.fromEx(ex)

			if isinstance(result, Result):
				return result

			return Result.fromObj(result)

		if _ResultObj.isExAvailable(self._obj):
			return Result.fromEx(_ResultObj.getEx(self._obj))

		child = Result(_handler={'then': handler}, _parent=self)
		self._child = weakref.proxy(child)
		return child

	def finally_(self, handler):
		assert self._child is None

		kwargs = {}

		if _ResultObj.isObjAvailable(self._obj):
			kwargs = {
				**kwargs, 'obj': _ResultObj.getObj(self._obj)
			}

		if _ResultObj.isExAvailable(self._obj):
			kwargs = {
				**kwargs, 'ex': _ResultObj.getEx(self._obj)
			}

		if kwargs:
			try:
				result = handler(**kwargs)
			except Exception as ex: # pylint: disable=broad-except
				return Result.fromEx(ex)

			if isinstance(result, Result):
				return result
			return Result.fromObj(result)

		return Result(_handler={'finally': handler}, _parent=self)

	def __repr__(self):
		return str(self)

	def __str__(self):
		return f'{type(self).__name__}({self._obj}, {self._handler})'

	@classmethod
	def fromObj(cls, obj):
		return cls(obj=_ResultObj(obj=obj))

	@classmethod
	def fromEx(cls, ex):
		return cls(obj=_ResultObj(ex=ex))

	@classmethod
	def fromExecute(cls, execute):
		return cls(obj=_ResultObj(execute=execute))


class _ResultObj:
	def __init__(self, obj=default, ex=default, execute=default):
		if obj is not default:
			assert ex is default
			assert execute is default
		elif ex is not default:
			assert obj is default
			assert execute is default
		elif execute is not default:
			assert obj is default
			assert ex is default
		else:
			assert False

		self._obj = obj
		self._ex = ex
		self._execute = execute

	@classmethod
	def checkEx(cls, obj):
		if not cls.isExAvailable(obj):
			return
		raise cls.getEx(obj)

	@classmethod
	def getObj(cls, obj):
		assert cls.isObjAvailable(obj), obj
		return obj._obj

	@classmethod
	def getEx(cls, obj):
		assert cls.isExAvailable(obj), obj
		return obj._ex

	@classmethod
	def getExecute(cls, obj):
		assert cls.isExecuteAvailable(obj), obj
		return obj._execute

	def __repr__(self):
		return str(self)

	@classmethod
	def isObjAvailable(cls, obj):
		if not cls._isObjAvailable(obj):
			return False
		return obj._obj is not default

	@classmethod
	def _isObjAvailable(cls, obj):
		return isinstance(obj, cls)

	@classmethod
	def isExAvailable(cls, obj):
		if not cls._isObjAvailable(obj):
			return False
		return obj._ex is not default

	@classmethod
	def isExecuteAvailable(cls, obj):
		if not cls._isObjAvailable(obj):
			return False
		return obj._execute is not default

	def __str__(self):
		if self.isObjAvailable(self):
			name = 'obj'
			value = self._obj
		elif self.isExAvailable(self):
			name = 'ex'
			value = self._ex
		elif self.isExecuteAvailable(self):
			name = 'execute'
			value = self._execute
		else:
			assert False
		return f'{type(self).__name__}({name}={value})'
