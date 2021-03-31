import sys

from actl.objects.object.exceptions import AAttributeNotFound, AAttributeIsNotSpecial

sys.setrecursionlimit(500)
_default = object()


class AObjectBase:
	def __init__(self, head):
		self._head = head

	def getAttribute(self, key):
		try:
			return self.lookupSpecialAttribute(key)
		except AAttributeIsNotSpecial(key).class_:
			pass
		
		try:
			getAttributeFunc = self.lookupAttributeInHead('__getAttribute__')
		except AAttributeNotFound('__getAttribute__').class_:
			getAttribute = self.lookupAttributeInClsSelf('__getAttribute__')
			bindGetAttribute = self.bindAttribute(getAttribute)
			getAttributeFunc = bindGetAttribute.call

		return getAttributeFunc(key)

	def lookupAttributeInClsSelf(self, key):
		class_ = self.getAttribute('__class__')
		parents = class_.getAttribute('__parents__')

		for cls in [class_, *parents]:
			self_ = cls.getAttribute('__self__')
			try:
				return self_[key]
			except KeyError:
				pass

		raise AAttributeNotFound(key)

	def lookupAttributeInHead(self, key):
		try:
			return self._head[key]
		except KeyError:
			pass

		raise AAttributeNotFound(key)

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

	def lookupSpecialAttribute(self, key):
		if key not in ('__class__', '__self__', '__parents__'):
			raise AAttributeIsNotSpecial(key)

		return self.lookupAttributeInHead(key)

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
