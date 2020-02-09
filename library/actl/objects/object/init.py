from actl.objects.object.exceptions import AKeyNotFound, AAttributeNotFound
from actl.objects.object.utils import loadPropIfNeed
from actl.objects.object.Object import Object


Object.setAttr('__name__', 'Object')


@Object.addPyMethod('fromPy')
def _(_, head):
	return type(Object)(head)


class _NativeClass(type(Object)):
	def __init__(self, initScope=None):
		if initScope is None:
			initScope = {}
		initScope.update({'__class__': self.__aCls})
		super().__init__(initScope)

	def __init_subclass__(cls):
		super().__init_subclass__()
		aCls = type(Object)()
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
	except AAttributeNotFound:
		pass
	attr = self.findAttr(key)
	return loadPropIfNeed(self, attr)


Object.setAttr('__getAttr__', _makeMethod('Object.__getAttr__', _Object__getAttr__))
Object.setAttr('__self__', _Self({}))
Object.getAttr('__self__').setItem(
	'__getAttr__', _makeMethod('Object.__self__.__getAttr__', _Object__getAttr__)
)


class BuildClass(type(Object)):
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
	self = type(Object)()
	self.setAttr('__class__', cls)
	return self


@BuildClass.addMethodToClass(Object, '__call__')
def _(cls, *args, **kwargs):
	return cls.getAttr('__init__').call(*args, **kwargs)


@BuildClass.addMethodToClass(Object, '__toStr__')
def _(self):
	from actl.objects import String

	name = self.getAttr('__name__')
	return String.call(f"class '{name}'")


@BuildClass.addMethod(Object, '__toStr__')
def _(self):
	from actl.objects import String

	name = self.getAttr('__class__').getAttr('__name__')
	scope = self._head   # pylint: disable=protected-access
	return String.call(f'{name}<{scope}>')


class _Super(_NativeClass):
	def __init__(self, parents, aSelf):
		super().__init__()
		self._parents = parents
		self._aSelf = aSelf

	def findAttr(self, key):
		for parent in self._parents:
			try:
				return parent.findAttr(key)
			except AAttributeNotFound:
				pass
		raise AAttributeNotFound(key=key)

	def getAttr(self, key):
		return loadPropIfNeed(self._aSelf, self.findAttr(key))

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
		raise AAttributeNotFound(key=key)
