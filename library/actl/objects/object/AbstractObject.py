import sys

from actl.objects.object.exceptions import AAttributeNotFound, AAttributeIsNotSpecial


sys.setrecursionlimit(500)
_default = object()


class AbstractObject:
	_specialAttrs = {
		'__class__': 'class_',
		'__getAttr__': '_getAttr'
	}

	def __init__(self, head):
		self._head = head

	@property
	def class_(self):
		return self._head['__class__']

	@property
	def _getAttr(self):
		return self.findAttr('__getAttr__').get(self)

	def getAttr(self, key):
		try:
			return self.getSpecialAttr(key)
		except AAttributeIsNotSpecial as ex:
			ex.check(key)

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
		except AAttributeNotFound as ex:
			ex.check(key)
			return False
		else:
			return True

	def findAttr(self, key):
		raise NotImplementedError

	def call(self, *args, **kwargs):
		func = self.getAttr('__call__').call
		return func(*args, **kwargs)

	def get(self, instance):
		get = self.getAttr('__get__')
		return get.call(instance)

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

	def __eq__(self, other):
		if not isinstance(other, AbstractObject):
			return False
		return self._head == other._head

	def __hash__(self):
		return hash(str(self))

	def __repr__(self):
		return str(self)

	def __str__(self):
		def toStr():
			from actl.objects.AToPy import AToPy  # pylint: disable=cyclic-import, import-outside-toplevel

			if id(self) in AbstractObject._stack:
				return '{...}'
			AbstractObject._stack.add(id(self))

			pyView = AToPy(self)
			asStr = str(pyView)
			return asStr

		if hasattr(AbstractObject, '_stack'):
			return toStr()

		AbstractObject._stack = set()
		try:
			asStr = toStr()
		finally:
			del AbstractObject._stack

		return asStr
