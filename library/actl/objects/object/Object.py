import sys

from actl.objects.object.exceptions import AAttributeNotFound, AKeyNotFound, AAttributeIsNotSpecial


sys.setrecursionlimit(500)
_default = object()


class _Object:
	def __init__(self, head):
		self._head = head

	def getAttr(self, key):
		try:
			return self._getSpecialAttr(key)
		except AAttributeIsNotSpecial:
			pass

		getAttr = self.getAttr('__getAttr__')
		return getAttr.call(key)

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
			ex = AAttributeNotFound(key=key)
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
		except AAttributeNotFound:
			raise ex

	def _getSpecialAttr(self, key):
		if key in ('__class__', '__self__'):
			return self._head[key]

		if key == '__super__':
			try:
				super_ = self._head[key]
			except KeyError:
				self_ = self.getAttr('__class__').getAttr('__self__')
				try:
					super_ = self_.getItem(key)
				except AKeyNotFound:
					raise AAttributeNotFound(key)
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

		raise AAttributeIsNotSpecial(key)

	def __repr__(self):
		return str(self)

	def __str__(self):
		def toStr():
			from actl.objects.AToPy import \
				AToPy  # pylint: disable=cyclic-import, import-outside-toplevel

			if id(self) in _Object._stack:
				return '{...}'
			_Object._stack.add(id(self))

			pyView = AToPy(self)
			asStr = str(pyView)
			return asStr

		if hasattr(_Object, '_stack'):
			return toStr()

		_Object._stack = set()
		asStr = toStr()
		del _Object._stack

		return asStr


Object = _Object({})
