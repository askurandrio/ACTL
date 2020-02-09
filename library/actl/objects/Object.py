import sys


sys.setrecursionlimit(500)
_default = object()


class AGenericKeyError(Exception):
	MSG = 'Generic Error: {key}'

	def __init__(self, msg='', key=None):
		if (key is not None) and (not msg):
			msg = self.MSG.format(key=key)
		super().__init__(msg)


class ANotFoundAttribute(AGenericKeyError):
	MSG = 'This attribute not found: {key}'


class AKeyNotFound(AGenericKeyError):
	MSG = 'This key not found: {key}'


def _loadPropIfNeed(self, val):
	try:
		prop = val.get
	except (ANotFoundAttribute, AttributeError):
		return val
	else:
		return prop(self)


class _Object:
	def __init__(self, head=None):
		if head is None:
			head = {}
		self._head = head

	def getAttr(self, key):
		try:
			return self._getSpecialAttr(key)
		except ANotFoundAttribute:
			pass
		return self.getAttr('__getAttr__').call(key)

	def setAttr(self, key, value=_default):
		if value is not _default:
			self._head[key] = value
			return None

		def decorator(value):
			self._head[key] = value
			return value

		return decorator

	def hasAttr(self, key):
		try:
			self.getAttr(key)
		except ANotFoundAttribute:
			return False
		else:
			return True

	def call(self, *args, **kwargs):
		return self.getAttr('__call__').call(*args, **kwargs)

	def equal(self, other):
		return self._head == other._head  # pylint: disable=protected-access

	def get(self, instance):
		return self.getAttr('__get__').call(instance)

	def toStr(self):
		return self.getAttr('__toStr__').call()

	def addPyMethod(self, name):
		def decorator(func):
			method = lambda *args, **kwargs: func(self, *args, **kwargs)
			setattr(self, name, method)
			return method

		return decorator

	def findAttr(self, key):
		try:
			return self._head[key]
		except KeyError:
			ex = ANotFoundAttribute(key=key)
		if self is Object:
			raise ex
		self_ = self.getAttr('__class__').getAttr('__self__')
		try:
			return self_.getItem(key)
		except AKeyNotFound:
			pass
		try:
			super_ = self.getAttr('__super__')
			return super_.findAttr(key)  # pylint: disable=protected-access
		except ANotFoundAttribute:
			raise ex

	def _getSpecialAttr(self, key):
		if key in ('__class__', '__self__'):
			return self._head[key]

		if key == '__super__':
			try:
				super_ = self._head[key]
			except KeyError:
				self_ = self.getAttr('__class__').getAttr('__self__')
				super_ = self_.getItem(key)
			return super_.get(self)

		if key == '__getAttr__':
			try:
				res = self._head['__getAttr__']
			except KeyError:
				cls = self.getAttr('__class__')
				self_ = cls.getAttr('__self__')
				try:
					res = self_.getItem('__getAttr__')
				except AKeyNotFound:
					super_ = self.getAttr('__super__')
					return super_.getAttr('__getAttr__')
			return res.get(self)
		raise ANotFoundAttribute(f'This is not special attrribute: {key}')

	def __repr__(self):
		return str(self)

	def __str__(self):
		if ('__name__' in self._head) and (('__parents__' in self._head) or (self is Object)):
			return f"class {self._head['__name__']}"
		#Todo: remove
		if hasattr(_Object, '__stack'):
			parent = False
		else:
			_Object.__stack = set()
			parent = True
		if self in _Object.__stack:
			return '{...}'

		_Object.__stack.add(self)
		selfInStr = f'{type(self).__name__}<{self._head}>'
		if parent:
			del _Object.__stack
		return selfInStr


Object = _Object()
Object.setAttr('__name__', 'Object')


@Object.addPyMethod('fromPy')
def _(_, head):
	return _Object(head)


class _NativeClass(_Object):
	def __init__(self, initScope=None):
		if initScope is None:
			initScope = {}
		initScope.update({'__class__': self.__aCls})
		super().__init__(initScope)

	def __init_subclass__(cls):
		super().__init_subclass__()
		aCls = _Object()
		aCls.setAttr('__class__', Object)
		aCls.setAttr('__parents__', [Object])
		aCls.setAttr('__name__', cls.__name__)
		cls.__aCls = aCls


class _NativeFunc(_NativeClass):
	def __init__(self, name, func):
		super().__init__()
		self._name = name
		self._func = func

	def call(self, *args, **kwargs):
		return self._func(*args, **kwargs)

	def __str__(self):
		return f'{type(self).__name__}<{self._name}>'

	@classmethod
	def wrap(cls, name):
		def decorator(func):
			return cls(name, func)
		return decorator


class _NativeProperty(_NativeClass):
	def __init__(self, fget):
		super().__init__()
		self._fget = fget

	def get(self, instance):
		return self._fget.call(instance)

	def __str__(self):
		return f'{type(self).__name__}({self._fget})'


def _makeMethod(name, func):
	func = _NativeFunc(name, func)
	@_NativeFunc.wrap(f'fget_{func}')
	def fget(instance):
		@_NativeFunc.wrap(f'fgetWrapper_{func}')
		def wrapper(*args, **kwargs):
			return func.call(instance, *args, **kwargs)
		return wrapper
	return _NativeProperty(fget)


class _Self(_NativeClass):
	def __init__(self, initHead):
		super().__init__()
		self._head = initHead

	def setItem(self, key, value):
		self._head[key] = value

	def getItem(self, key):
		try:
			return self._head[key]
		except KeyError:
			raise AKeyNotFound(key=key)

	def __str__(self):
		return f'{type(self).__name__}<{self._head}>'


def _Object__getAttr__(self, key):
	try:
		return self._getSpecialAttr(key)  # pylint: disable=protected-access
	except ANotFoundAttribute:
		pass
	attr = self.findAttr(key)
	return _loadPropIfNeed(self, attr)


Object.setAttr('__getAttr__', _makeMethod('Object.__getAttr__', _Object__getAttr__))
Object.setAttr('__self__', _Self({}))
Object.getAttr('__self__').setItem(
	'__getAttr__', _makeMethod('Object.__self__.__getAttr__', _Object__getAttr__)
)


class BuildClass(_Object):
	def __init__(self, name, parents=None):
		super().__init__()
		if parents is None:
			parents = []
		parents.append(Object)
		self.setAttr('__class__', Object)
		self.setAttr('__parents__', parents)
		self.setAttr('__name__', name)
		self.setAttr('__super__', _Super.make(parents))
		self.setAttr('__self__', _Self({'__super__': _SuperSelf.make(parents)}))

	def addMethod(self, name):
		def decorator(func):
			cls_name = self.getAttr('__name__')
			cls_name = cls_name[0].lower() + cls_name[1:]
			func.__name__ = f'{cls_name}.{name}'
			method = _makeMethod(func.__name__, func)
			self.getAttr('__self__').setItem(name, method)
			return func

		return decorator

	def addMethodToClass(self, name):
		def decorator(func):
			cls_name = self.getAttr('__name__')
			func.__name__ = f'{cls_name}.{name}'
			method = _makeMethod(func.__name__, func)
			self.setAttr(name, method)
			return func

		return decorator


@BuildClass.addMethodToClass(Object, '__init__')
def _(cls):
	self = _Object()
	self.setAttr('__class__', cls)
	return self


@BuildClass.addMethodToClass(Object, '__call__')
def _(cls, *args, **kwargs):
	return cls.getAttr('__init__').call(*args, **kwargs)


@BuildClass.addMethodToClass(Object, '__toStr__')
def _(self):
	name = self.getAttr('__name__')
	return f"class '{name}'"


@BuildClass.addMethod(Object, '__toStr__')
def _(self):
	name = self.getAttr('__class__').getAttr('__name__')
	scope = self._head   # pylint: disable=protected-access
	return f'{name}<{scope}>'


class _Super(_NativeClass):
	def __init__(self, parents, aSelf):
		super().__init__()
		self._parents = parents
		self._aSelf = aSelf

	def findAttr(self, key):
		for parent in self._parents:
			try:
				return parent.findAttr(key)
			except ANotFoundAttribute:
				pass
		raise ANotFoundAttribute(key=key)

	def getAttr(self, key):
		return _loadPropIfNeed(self._aSelf, self.findAttr(key))

	@classmethod
	def make(cls, parents):
		@_NativeFunc.wrap(f'fget_{cls.__name__}')
		def fget(aSelf):
			return cls(parents, aSelf)
		return _NativeProperty(fget)

	def __str__(self):
		return f'{type(self).__name__}<{self._parents}>'


class _SuperSelf(_Super):
	def __init__(self, parents, aSelf):
		super().__init__(parents, aSelf)
		self._parents = [parent.getAttr('__self__') for parent in self._parents]

	def findAttr(self, key):
		for parent in self._parents:
			try:
				return parent.getItem(key)
			except AKeyNotFound:
				pass
		raise ANotFoundAttribute(key=key)
