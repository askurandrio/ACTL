import sys

from actl.utils import default
from actl.objects.object.Result import Result
from actl.objects.object.exceptions import AAttributeIsNotSpecial, AAttributeNotFound
from actl.opcodes.opcodes import RETURN


sys.setrecursionlimit(500)


class AObject:
	Function = None

	def __init__(self, head):
		self._head = head

	@property
	def getAttribute(self):
		getAttribute = self.lookupSpecialAttribute('__getAttribute__')

		return getAttribute.call

	@property
	def _getAttribute(self):
		try:
			return Result.fromObj(self.lookupAttributeInHead('__getAttribute__'))
		except AAttributeNotFound('__getAttribute__').class_:
			pass

		getAttribute = self.lookupAttributeInClsSelf('__getAttribute__')
		return self.bindAttribute(getAttribute)

	@property
	def get(self):
		get = self.getAttribute('__get__')

		return get.call

	@property
	def _superGetAttribute(self):
		try:
			return Result.fromObj(self.lookupAttributeInHead('__superGetAttribute__'))
		except AAttributeNotFound('__superGetAttribute__').class_:
			pass

		superGetAttribute = self.lookupAttributeInClsSelf('__superGetAttribute__')
		return self.bindAttribute(superGetAttribute)

	@property
	def super_(self):
		superGetAttribute = self.lookupSpecialAttribute('__superGetAttribute__')

		return superGetAttribute.call

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
			result = self.getAttribute(key)
			if isinstance(result, Result):
				result.obj
		except AAttributeNotFound(key).class_:
			return False
		else:
			return True

	@property
	def call(self):
		call = self.getAttribute('__call__')

		return call.call

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

		if key == '__getAttribute__':
			return self._getAttribute

		if key == '__superGetAttribute__':
			return self._superGetAttribute

		raise AAttributeIsNotSpecial(key)

	def isinstance_(self, cls):
		if self.class_ == cls:
			return True

		for parent in self.class_.parents:
			if parent == cls:
				return True

		return False

	def bindAttribute(self, attribute):
		if not isinstance(attribute, AObject):
			return Result.fromObj(attribute)

		resultAttributeGet = attribute.get

		@resultAttributeGet.finally_
		def result(obj=default, ex=default):
			if ex is not default:
				if not isinstance(ex, AAttributeNotFound('__get__').class_):
					raise ex

				if attribute.isinstance_(self.Function):
					applyFunc = attribute.getAttribute('apply').call.obj
					return applyFunc(self).obj

				return attribute

			return obj.call(self)

		return result

	def toPyString(self):
		name = self.getAttribute('__class__').obj.getAttribute('__name__').obj
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
		if not hasattr(AObject, '_stack'):
			AObject._stack = set()

			try:
				return str(self)
			finally:
				del AObject._stack

		if id(self) in AObject._stack:
			return '{...}'

		AObject._stack.add(id(self))

		try:
			from actl.objects.String import String  # pylint: disable=cyclic-import, import-outside-toplevel

			string = String.call(self).obj
			return string.toPyString()
		except Exception as ex:
			return f'Error during convert<{id(self)}> to string: {ex}'
