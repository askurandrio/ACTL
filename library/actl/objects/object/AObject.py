from actl.objects.object.exceptions import AAttributeNotFound
from actl.objects.object.AObjectBase import AObjectBase


class AObject(AObjectBase):
	def lookupAttribute(self, key):
		try:
			return super().lookupAttribute(key)
		except AAttributeNotFound(key).class_:
			pass

		class_ = self.getAttribute('__class__')
		try:
			return class_.lookupAttributeInSelf(key, self)
		except AAttributeNotFound(key).class_:
			pass

		return self.super_(class_, key)

	def _toString(self):
		import actl.objects  # pylint: disable=cyclic-import, import-outside-toplevel

		if id(self) in AObject._stack:
			return '{...}'
		AObject._stack.add(id(self))

		try:
			string = actl.objects.String(self)
			return string.toPyString()
		except Exception as ex:
			return f'Error during convert to String: {ex}'

	def __eq__(self, other):
		if not isinstance(other, AObject):
			return False
		return self.head == other.head

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
