import sys
import traceback

from actl.objects.object.executeSyncCoroutine import executeSyncCoroutine
from actl.objects.object.exceptions import AAttributeIsNotSpecial, AAttributeNotFound


sys.setrecursionlimit(500)


class AObject:
	Function = None
	Object = None
	String = None

	def __init__(self, head):
		self._head = head

	async def getAttribute(self, name):
		try:
			return await self.lookupSpecialAttribute(name)
		except AAttributeIsNotSpecial(key=name).class_:
			pass

		getAttribute = await self.getAttribute('__getAttribute__')

		return await getAttribute.call(name)

	async def _get_getAttribute(self):
		try:
			return self.lookupAttributeInHead('__getAttribute__')
		except AAttributeNotFound('__getAttribute__').class_:
			pass

		getAttribute = self.lookupAttributeInClsSelf('__getAttribute__')
		return await self.bindAttribute(getAttribute)

	async def get(self, instance):
		get = await self.getAttribute('__get__')

		return await get.call(instance)

	async def _get_superGetAttribute(self):
		try:
			return self.lookupAttributeInHead('__superGetAttribute__')
		except AAttributeNotFound('__superGetAttribute__').class_:
			pass

		superGetAttribute = self.lookupAttributeInClsSelf('__superGetAttribute__')
		return await self.bindAttribute(superGetAttribute)

	async def super_(self, for_, name):
		superGetAttribute = await self.lookupSpecialAttribute('__superGetAttribute__')
		return await superGetAttribute.call(for_, name)

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

	async def hasAttribute(self, key):
		try:
			await self.getAttribute(key)
		except AAttributeNotFound(key).class_:
			return False
		else:
			return True

	async def call(self, *args, **kwargs):
		call = await self.getAttribute('__call__')

		return await call.call(*args, **kwargs)

	@property
	def class_(self):
		return self.lookupAttributeInHead('__class__')

	@property
	def self_(self):
		return self.lookupAttributeInHead('__self__')

	@property
	def parents(self):
		return self.lookupAttributeInHead('__parents__')

	async def lookupSpecialAttribute(self, key):
		if key == '__class__':
			return self.class_

		if key == '__self__':
			return self.self_

		if key == '__parents__':
			return self.parents

		if key == '__getAttribute__':
			return await self._get_getAttribute()

		if key == '__superGetAttribute__':
			return await self._get_superGetAttribute()

		raise AAttributeIsNotSpecial(key)

	def isinstance_(self, instance):
		if instance.class_ == self:
			return True

		for parent in instance.class_.parents:
			if parent == self:
				return True

		return False

	async def bindAttribute(self, attribute):
		if not isinstance(attribute, AObject):
			return attribute

		if await attribute.hasAttribute('__get__'):
			return await attribute.get(self)

		if self.Function.isinstance_(attribute):
			applyFunc = await attribute.getAttribute('apply')
			return await applyFunc.call(self)

		return attribute

	async def toPyString(self):
		if not hasattr(AObject, '_stringSeen'):
			AObject._stringSeen = set()

			try:
				return await self.toPyString()
			finally:
				del AObject._stringSeen

		AObject._stringSeen.add(id(self))

		name = await self.class_.getAttribute('__name__')
		selfToStr = f'{name}<'

		for key, value in self._head.items():
			if key == '__class__':
				continue

			if id(value) in AObject._stringSeen:
				reprValue = '↑...'
			else:
				AObject._stringSeen.add(id(value))
				reprValue = repr(value)

			selfToStr = f'{selfToStr}{key}={reprValue}, '

		if selfToStr[-2:] == ', ':
			selfToStr = selfToStr[:-2]

		return f'{selfToStr}>'

	def __eq__(self, other):
		if not isinstance(other, AObject):
			return False
		return self._head == other._head

	def __hash__(self):
		return hash(str(self))

	def __repr__(self):
		return str(self)

	def __str__(self):
		try:
			string = executeSyncCoroutine(self.String.call(self))
			pyString = executeSyncCoroutine(string.toPyString())
			return pyString
		except Exception as ex:  # pylint: disable=broad-except
			traceback.print_exc()
			return f'Error during convert<{id(self)}> to string: {ex}'
