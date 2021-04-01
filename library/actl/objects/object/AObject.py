import sys

from actl.objects.object.exceptions import AAttributeIsNotSpecial, AAttributeNotFound


sys.setrecursionlimit(500)


class AObject:
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

	def bindAttribute(self, attribute):
		if not isinstance(attribute, AObject):
			return attribute

		try:
			attributeGet = attribute.get
		except AAttributeNotFound('__get__').class_:
			return attribute

		attributeGetCall = attributeGet.call
		return attributeGetCall(self)

	def _toString(self):
		from actl.objects.String import String  # pylint: disable=cyclic-import, import-outside-toplevel

		if id(self) in AObject._stack:
			return '{...}'
		AObject._stack.add(id(self))

		string = String.call(self)
		return string.toPyString()

	def toPyString(self):
		name = self.getAttribute('__class__').getAttribute('__name__')
		head = self._head
		head = {key: value for key, value in head.items() if key != '__class__'}
		return f'{name}<{head}>'

	def __eq__(self, other):
		if not isinstance(other, AObject):
			return False
		return self._head == other._head

	def __hash__(self):
		return hash(str(self))

	def __repr__(self):
		return str(self)

	def __str__(self):
		if hasattr(AObject, '_stack'):
			return self._toString()

		AObject._stack = set()

		try:
			asStr = self._toString()
		finally:
			del AObject._stack

		return asStr
