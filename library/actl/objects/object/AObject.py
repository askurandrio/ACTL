import traceback

from actl.utils import ReprToStr, executeSyncCoroutine
from actl.objects.object.exceptions import AAttributeNotFound
from actl.signals import onSignal


class _MethodGetterView:
	def __init__(self, attributeName, pyAttributeName):
		self._attributeName = attributeName
		self._pyAttributeName = pyAttributeName

	def __get__(self, obj, _):
		pyMethod = getattr(obj, self._pyAttributeName)
		return _MethodView(self._attributeName, pyMethod, obj)


class _MethodView(ReprToStr):
	def __init__(self, attributeName, pyMethod, obj):
		self._attributeName = attributeName
		self.pyMethod = pyMethod
		self._obj = obj

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False

		return self.pyMethod == other.pyMethod

	def __call__(self, *args, **kwargs):
		return self.pyMethod(*args, **kwargs)

	def __str__(self):
		return f'{self._obj}.{self._attributeName}'


class AObject(ReprToStr):
	_default = object()
	call = _MethodGetterView('__call__', '_call')

	def __init__(self, head):
		self._head = head

	async def getAttribute(self, name):
		attribute, isSuccess = await self.lookupSpecialAttribute(name)
		if isSuccess:
			return attribute

		getAttribute = await self.getAttribute('__getAttribute__')

		return await getAttribute.call(name)

	async def _get_getAttribute(self):
		getAttribute, isSuccess = self.lookupAttributeInHead('__getAttribute__')
		if isSuccess:
			return getAttribute, True

		getAttribute, isSuccess = self.lookupAttributeInClsSelf('__getAttribute__')
		if isSuccess:
			bindedGetAttribute = await self.bindAttribute(getAttribute)
			return bindedGetAttribute, True

		return None, False

	async def get(self, instance):
		get = await self.getAttribute('__get__')

		return await get.call(instance)

	async def _get_superGetAttribute(self):
		superGetAttribute, isSuccess = self.lookupAttributeInHead(
			'__superGetAttribute__'
		)
		if superGetAttribute:
			return superGetAttribute, True

		superGetAttribute, isSuccess = self.lookupAttributeInClsSelf(
			'__superGetAttribute__'
		)
		if isSuccess:
			bindedSuperGetAttribute = await self.bindAttribute(superGetAttribute)
			return bindedSuperGetAttribute, True

		return None, False

	async def super_(self, for_, name):
		superGetAttribute, isSuccess = await self.lookupSpecialAttribute(
			'__superGetAttribute__'
		)
		AAttributeNotFound.check(isSuccess, key='__superGetAttribute__')
		return await superGetAttribute.call(for_, name)

	def lookupAttributeInClsSelf(self, key):
		class_ = self.class_
		parents = class_.parents

		for cls in [class_, *parents]:
			self_ = cls.self_
			try:
				return self_[key], True
			except KeyError:
				pass

		return None, False

	def lookupAttributeInHead(self, key):
		attribute = self._head.get(key, self._default)

		if attribute is self._default:
			return None, False

		return attribute, True

	def setAttribute(self, key, value):
		self._head[key] = value

	async def hasAttribute(self, key):
		try:
			await self.getAttribute(key)
		except AAttributeNotFound.class_(key):
			return False
		else:
			return True

	async def _call(self, *args, **kwargs):
		call = await self.getAttribute('__call__')

		return await call.call(*args, **kwargs)

	@property
	def class_(self):
		class_, isSucess = self.lookupAttributeInHead('__class__')
		AAttributeNotFound.check(isSucess, key='__class__')
		return class_

	@property
	def self_(self):
		self_, isSucess = self.lookupAttributeInHead('__self__')
		AAttributeNotFound.check(isSucess, key='__self__')
		return self_

	@property
	def parents(self):
		parents, isSucess = self.lookupAttributeInHead('__parents__')
		AAttributeNotFound.check(isSucess, key='__parents__')
		return parents

	async def lookupSpecialAttribute(self, key):
		if key == '__class__':
			return self.class_, True

		if key == '__self__':
			return self.self_, True

		if key == '__parents__':
			return self.parents, True

		if key == '__getAttribute__':
			return await self._get_getAttribute()

		if key == '__superGetAttribute__':
			return await self._get_superGetAttribute()

		return None, False

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

	def __str__(self):
		try:
			string = executeSyncCoroutine(self.String.call(self))
			pyString = executeSyncCoroutine(string.toPyString())
			return pyString
		except Exception as ex:  # pylint: disable=broad-except
			traceback.print_exc()

			try:
				selfToStr = str(self._head)
			except Exception:  # pylint: disable=broad-except
				selfToStr = id(self)

			return f'Error during convert<{selfToStr}> to string: {type(ex)} "{ex}"'


@onSignal('actl.Function:created')
async def _onFunctionCreated(Function):
	AObject.Function = Function


@onSignal('actl.Object:created')
async def _onObjectCreated(Object):
	AObject.Object = Object


@onSignal('actl.String:created')
async def _onStringCreated(String):
	AObject.String = String
