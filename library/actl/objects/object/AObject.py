import sys

from actl.objects.object.utils import loadPropIfNeed
from actl.objects.object.exceptions import AAttributeNotFound, AAttributeIsNotSpecial, AKeyNotFound


sys.setrecursionlimit(500)
_default = object()


class _GetDescriptor:
	def __get__(_, obj, _1):
		get = obj.getAttr('__get__')
		return get.call


class AObject:
	get = _GetDescriptor()
	_specialAttrs = {
		'__class__': '_class',
		'__getAttr__': '_getAttr',
		'__self__': '_self',
	}

	def __init__(self, head):
		self._head = head

	@property
	def _class(self):
		return self._head['__class__']

	@property
	def _getAttr(self):
		return self.findAttr('__getAttr__').get(self)

	@property
	def _self(self):
		return self._head['__self__']

	def getAttr(self, key):
		try:
			return self.getSpecialAttr(key)
		except AAttributeIsNotSpecial:
			pass

		return self._getAttr.call(key)

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
		except AAttributeNotFound:
			return False
		else:
			return True

	def findAttr(self, key):
		raise NotImplementedError

	def call(self, *args, **kwargs):
		func = self.getAttr('__call__').call
		return func(*args, **kwargs)

	def addPyMethod(self, name):
		def decorator(func):
			method = lambda *args, **kwargs: func(self, *args, **kwargs)
			setattr(self, name, method)
			return method

		return decorator

	def getSpecialAttr(self, key):
		try:
			propertyName = self._specialAttrs[key]
		except KeyError:
			raise AAttributeIsNotSpecial(key)

		return getattr(self, propertyName)

	def super_(self, for_, key, bind=True):
		isClass = self._head.get('__isClass__')
		if isClass:
			parents = self._head['__parents__']
		else:
			parents = self.getAttr('__class__').getAttr('__parents__')

		if for_ in parents:
			parents = parents[parents.index(for_) + 1:]

		for parent in parents:
			if isClass:
				try:
					prop = parent.findAttr(key)
				except AAttributeNotFound:
					continue
			else:
				try:
					prop = parent.getAttr('__self__').getItem(key)
				except AKeyNotFound:
					continue
			if bind:
				prop = loadPropIfNeed(self, prop)
			return prop
		raise AAttributeNotFound(key)

	def findAttr(self, key):
		try:
			return self._head[key]
		except KeyError:
			pass

		if self._head.get('__isClass__'):
			return self.super_(self, key, bind=False)

		self_ = self.getAttr('__class__').getAttr('__self__')
		try:
			return self_.getItem(key)
		except AKeyNotFound:
			pass
		try:
			return self.super_(self.getAttr('__class__'), key, bind=False)
		except AAttributeNotFound:
			raise AAttributeNotFound(key=key)

	def __eq__(self, other):
		if not isinstance(other, AObject):
			return False
		return self._head == other._head

	def __hash__(self):
		return hash(str(self))

	def __repr__(self):
		return str(self)

	def __str__(self):
		def toStr():
			from actl.objects.AToPy import AToPy  # pylint: disable=cyclic-import, import-outside-toplevel

			if id(self) in AObject._stack:
				return '{...}'
			AObject._stack.add(id(self))

			pyView = AToPy(self)
			asStr = str(pyView)
			return asStr

		if hasattr(AObject, '_stack'):
			return toStr()

		AObject._stack = set()
		try:
			asStr = toStr()
		finally:
			del AObject._stack

		return asStr
