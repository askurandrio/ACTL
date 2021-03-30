import sys

from actl.objects.object.exceptions import AAttributeNotFound, AAttributeIsNotSpecial

sys.setrecursionlimit(500)
_default = object()


class AObjectBase:
	def __init__(self, head):
		self._head = head

	def getAttribute(self, key):
		try:
			return self._lookupSpecialAttribute(key)
		except AAttributeIsNotSpecial(key).class_:
			pass

		getAttribute = self.lookupAttribute('__getAttribute__')
		getAttributeCall = getAttribute.call
		return getAttributeCall(key)

	def setAttribute(self, key, value):
		self._head[key] = value

	def hasAttribute(self, key):
		try:
			self.getAttribute(key)
		except AAttributeNotFound(key).class_:
			return False
		else:
			return True

	def call(self, *args, **kwargs):
		func = self.getAttribute('__call__')
		funcCall = func.call
		return funcCall(*args, **kwargs)

	def _lookupSpecialAttribute(self, key):
		if key != '__class__':
			raise AAttributeIsNotSpecial(key)

		try:
			return self._head[key]
		except KeyError as ex:
			raise AAttributeNotFound(key=key) from ex

	def lookupAttribute(self, key):
		try:
			return self._lookupSpecialAttribute(key)
		except AAttributeIsNotSpecial(key).class_:
			pass

		try:
			return self._head[key]
		except KeyError:
			pass

		raise AAttributeNotFound(key=key)

	def __eq__(self, other):
		if not isinstance(other, AObjectBase):
			return False
		return self._head == other._head

	def __hash__(self):
		return hash(str(self))

	def __repr__(self):
		return str(self)

	def __str__(self):
		def toStr():
			from actl.objects.AToPy import \
				AToPy  # pylint: disable=cyclic-import, import-outside-toplevel

			if id(self) in AObjectBase._stack:
				return '{...}'
			AObjectBase._stack.add(id(self))

			pyView = AToPy(self)
			asStr = str(pyView)
			return asStr

		if hasattr(AObjectBase, '_stack'):
			return toStr()

		AObjectBase._stack = set()
		try:
			asStr = toStr()
		finally:
			del AObjectBase._stack

		return asStr
