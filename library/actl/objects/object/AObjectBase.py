import sys

from actl.objects.object.exceptions import AAttributeNotFound, AAttributeIsNotSpecial

sys.setrecursionlimit(500)
_default = object()


class AObjectBase:
	def __init__(self, head):
		self._head = head

	@property
	def getAttribute(self):
		try:
			getAttributeFunc = self.lookupAttributeInHead('__getAttribute__')
		except AAttributeNotFound('__getAttribute__').class_:
			getAttribute = self.lookupAttributeInClsSelf('__getAttribute__')
			getAttributeFunc = self.bindAttribute(getAttribute)

		return getAttributeFunc.call

	@property
	def get(self):
		get = self.getAttribute('__get__')
		return get.call

	@property
	def super_(self):
		try:
			superGetAttributeFunc = self.lookupAttributeInHead('__superGetAttribute__')
		except AAttributeNotFound('__superGetAttribute__').class_:
			superGetAttribute = self.lookupAttributeInClsSelf('__superGetAttribute__')
			bindSuperGetAttribute = self.bindAttribute(superGetAttribute)
			superGetAttributeFunc = bindSuperGetAttribute.call

		return superGetAttributeFunc

	def lookupAttributeInClsSelf(self, key):
		class_ = self.class_
		parents = class_.parents

		for cls in [class_, *parents]:
			self_ = cls.self_
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

	@property
	def call(self):
		func = self.getAttribute('__call__')
		return func.call

	@property
	def class_(self):
		return self.lookupAttributeInHead('__class__')

	@property
	def self_(self):
		return self.lookupAttributeInHead('__self__')

	@property
	def parents(self):
		return self.lookupAttributeInHead('__parents__')

	def lookupSpecialAttribute(self, key):
		if key == '__class__':
			return self.class_
		
		if key == '__self__':
			return self.self_

		if key == '__parents__':
			return self.parents

		raise AAttributeIsNotSpecial(key)

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
