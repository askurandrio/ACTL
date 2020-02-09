import sys

from actl.objects.object.exceptions import AAttributeNotFound, AKeyNotFound


sys.setrecursionlimit(500)
_default = object()


class _Object:
	def __init__(self, head=None):
		if head is None:
			head = {}
		self._head = head

	def getAttr(self, key):
		try:
			return self._getSpecialAttr(key)
		except AAttributeNotFound:
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
		raise AAttributeNotFound(f'This is not special attrribute: {key}')

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
