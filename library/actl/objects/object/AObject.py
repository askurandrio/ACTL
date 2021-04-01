from actl.objects.object.exceptions import AAttributeIsNotSpecial, AAttributeNotFound
from actl.objects.object.AObjectBase import AObjectBase


class AObject(AObjectBase):
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
