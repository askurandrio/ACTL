import weakref

import sys
sys.setrecursionlimit(100)


class _Object:
	def __init__(self, initScope=None):
		if initScope is None:
			initScope = {}
		self._scope = initScope

	def getAttr(self, key):
		return self._getAttr(key)

	def setAttr(self, key, value):
		self._scope[key] = value

	@property
	def call(self, *args, **kwargs):
		return self.getAttr('__call__').call

	@property
	def get(self, *args, **kwargs):
		return self.getAttr('__get__').call

	@property
	def toStr(self):
		return self.getAttr('__toStr__').call

	def addFromPy(self, func):
		self.fromPy = func
		return func

	def _findAttr(self, key):
		try:
			return self._scope[key]
		except KeyError as ex:
			pEx = ex
		if key == '__class__':
			raise pEx
		if self is Object:
			raise pEx
		self_ = self.getAttr('__class__').getAttr('__self__')
		try:
			return self_._findAttr(key)
		except KeyError:
			pass
		if key == '__super__':
			raise pEx
		try:
			super_ = self.getAttr('__super__')
			return super_._findAttr(key)
		except KeyError:
			raise pEx
	
	def _getAttr(self, key):
		val = self._findAttr(key)
		try:
			val = val.get
		except (KeyError, AttributeError):
			pass
		else:
			val = val(self)
		return val

	def __repr__(self):
		return str(self)
	
	def __str__(self):
		try:
			return self.toStr()
		except RecursionError:
			import pdb; pdb.set_trace()
			self.toStr()

	
Object = _Object()
Object.setAttr('__name__', 'Object')
Object.setAttr('__class__', weakref.proxy(Object))


class _NativeClass(_Object):
	def __init__(self, initScope=None):
		try:
			cls = self.__cls
		except AttributeError:
			self._makeCls()
			cls = self.__cls
		if initScope is None:
			initScope = {}
		initScope.update({'__class__': cls})
		super().__init__(initScope)
		
	@classmethod
	def _makeCls(cls):
		child = _Object()
		child.setAttr('__class__', Object)
		child.setAttr('__parents__', [Object])
		child.setAttr('__name__', cls.__name__)
		cls.__cls = child


class _Self(_NativeClass):
	def __init__(self, scope):
		super().__init__(scope)

	def _findAttr(self, key):
		return self._scope[key]

	def toStr(self):
		return f'{type(self).__name__}<{self._scope}>'


Object.setAttr('__self__', _Self({}))


class _NativeFunc(_NativeClass):
	def __init__(self, name, func):
		super().__init__()
		self._name = name
		self._func = func
	
	def call(self, *args, **kwargs):
		return self._func(*args, **kwargs)

	def toStr(self):
		return self._name

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

	def toStr(self):
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


class BuildClass(_Object):
	def __init__(self, name, parents=None):
		super().__init__()
		if parents is None:
			parents = []
		parents.append(Object)
		self.setAttr('__class__', Object)
		self.setAttr('__parents__', parents)
		self.setAttr('__name__', name)
		self.setAttr('__super__', _Super(self))
		self.setAttr('__self__', _Self({'__super__': _SuperSelf}))
	
	def addMethod(self, name):
		def decorator(func):
			cls_name = self.getAttr('__name__')
			cls_name = cls_name[0].lower() + cls_name[1:]
			method = _makeMethod(f'{cls_name}.{name}', func)
			self.getAttr('__self__').setAttr(name, method)
			return func
		
		return decorator
	
	def addMethodToClass(self, name):
		def decorator(func):
			cls_name = self.getAttr('__name__')
			method = _makeMethod(f'{cls_name}.{name}', func)
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
@BuildClass.addMethod(Object, '__toStr__')
def _(self):
	def isClass():
		try:
			self.getAttr('__self__')
			(self is Object) or self.getAttr('__parents__')
		except KeyError:
			return False
		return True
	if isClass():
		name = self.getAttr('__name__')
		return f"class '{name}'"
	name = self.getAttr('__class__').getAttr('__name__')
	scope = self._scope
	return f'{name}<{scope}>'


class _Super(_NativeClass):
	def __init__(self, instance):
		super().__init__()
		self._instance = instance

	def _findAttr(self, key):
		for parent in self._instance.getAttr('__parents__'):
			try:
				return parent._findAttr(key)
			except KeyError:
				pass
		raise KeyError(f'Super doesnt have key: {key}')
	
	def toStr(self):
		return f'{type(self).__name__}<>'


def _wrapSuperSelf(cls):
	return _NativeProperty(_NativeFunc('fget_SuperSelf', lambda self_: cls(self_)))


@_wrapSuperSelf
class _SuperSelf(_Super):
	def _findAttr(self, key):
		for parent in self._instance.getAttr('__class__').getAttr('__parents__'):
			self_ = parent.getAttr('__self__')
			try:
				return self_._findAttr(key)
			except KeyError:
				continue
		raise KeyError(f'Super doesnt have key: {key}')
