from calendar import c
import imp


import os
import traceback

from actl.signals import onSignal
from actl.utils import ReprToStr, executeSyncCoroutine
from actl.objects.object.exceptions import AAttributeNotFound


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


class _GetAttributeView(ReprToStr):
	_default = object()

	def __init__(self, obj):
		self._obj = obj

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False

		return self._obj == other._obj

	async def __call__(self, name):
		attribute, found = await self.lookupSpecialAttribute(name)
		if found:
			return attribute

		getAttribute = await self('__getAttribute__')

		return await getAttribute.call(name)

	async def lookupSpecialAttribute(self, name):
		if not isinstance(name, str):
			return None, False

		if name.startswith('_'):
			resolve_name = f'_resolve{name}'
		else:
			resolve_name = f'_resolve_{name}'

		resolve_method = getattr(self._obj, resolve_name, None)
		if resolve_method is not None:
			return await resolve_method(), True

		return None, False

	def lookupAttributeInHead(self, key):
		attribute = self._obj.head.get(key, self._default)

		if attribute is self._default:
			return None, False

		return attribute, True

	async def lookupAttributeInClsSelf(self, key):
		async def classes():
			class_ = await self('__class__')
			yield class_

			for cls in await class_.getAttribute('__parents__'):
				yield cls

		async for cls in classes():
			self_ = await cls.getAttribute('__self__')
			try:
				return self_[key], True
			except KeyError:
				pass

		return None, False

	async def bind(self, attribute):
		if not isinstance(attribute, AObject):
			return attribute

		if await self.Function.isinstance_(attribute):
			applyFunc = await attribute.getAttribute('apply')
			return await applyFunc.call(self._obj)

		if await attribute.hasAttribute('__get__'):
			return await attribute.get(self._obj)

		return attribute

	def __str__(self):
		return f'{self._obj}.getAttribute'


class AObject(ReprToStr):
	def __init__(self, head):
		self.head = head

	async def _resolve__getAttribute__(self):
		getAttribute, isSuccess = self.getAttribute.lookupAttributeInHead(
			'__getAttribute__'
		)
		if isSuccess:
			return getAttribute

		getAttribute, isSuccess = await self.getAttribute.lookupAttributeInClsSelf(
			'__getAttribute__'
		)
		if isSuccess:
			bindedGetAttribute = await self.getAttribute.bind(getAttribute)
			return bindedGetAttribute

		return None

	async def get(self, instance):
		get = await self.getAttribute('__get__')

		return await get.call(instance)

	async def _resolve__superGetAttribute__(self):
		superGetAttribute, isSuccess = self.getAttribute.lookupAttributeInHead(
			'__superGetAttribute__'
		)
		if superGetAttribute:
			return superGetAttribute

		superGetAttribute, isSuccess = await self.getAttribute.lookupAttributeInClsSelf(
			'__superGetAttribute__'
		)
		if isSuccess:
			bindedSuperGetAttribute = await self.getAttribute.bind(superGetAttribute)
			return bindedSuperGetAttribute

		return None

	async def super_(self, for_, name):
		superGetAttribute, isSuccess = await self.getAttribute.lookupSpecialAttribute(
			'__superGetAttribute__'
		)
		AAttributeNotFound.check(isSuccess, key='__superGetAttribute__')
		return await superGetAttribute.call(for_, name)

	async def setAttribute(self, key, value):
		setAttribute = await self.getAttribute('__setAttribute__')
		await setAttribute.call(key, value)

	async def hasAttribute(self, key):
		try:
			await self.getAttribute(key)
		except AAttributeNotFound.class_(key):
			return False
		else:
			return True

	@property
	def call(self):
		return _MethodView('__call__', self._call, self)

	@property
	def getAttribute(self):
		return _GetAttributeView(self)

	async def _call(self, *args, **kwargs):
		call = await self.getAttribute('__call__')

		return await call.call(*args, **kwargs)

	async def _resolve__class__(self):
		class_, isSucess = self.getAttribute.lookupAttributeInHead('__class__')
		AAttributeNotFound.check(isSucess, key='__class__')
		return class_

	async def _resolve__self__(self):
		self_, isSucess = self.getAttribute.lookupAttributeInHead('__self__')
		AAttributeNotFound.check(isSucess, key='__self__')
		return self_

	async def _resolve__parents__(self):
		parents, isSucess = self.getAttribute.lookupAttributeInHead('__parents__')
		AAttributeNotFound.check(isSucess, key='__parents__')
		return parents

	async def isinstance_(self, instance):
		class_ = await instance.getAttribute('__class__')

		if class_ == self:
			return True

		parents = await class_.getAttribute('__parents__')
		for parent in parents:
			if parent == self:
				return True

		return False

	def __eq__(self, other):
		if not isinstance(other, AObject):
			return False
		return self.head == other.head

	def __hash__(self):
		return hash(str(self))

	def __str__(self):
		try:
			string = executeSyncCoroutine(AObject.String.call(self))
			toPyStringMethod = executeSyncCoroutine(string.getAttribute('toPyString'))
			pyString = executeSyncCoroutine(toPyStringMethod.call())
			return pyString
		except Exception as ex:  # pylint: disable=broad-except
			traceback.print_exc()

			if 'RERAISE_STR_ERROR' in os.environ:
				raise

			try:
				selfToStr = str(self.head)
			except Exception:  # pylint: disable=broad-except
				selfToStr = id(self)

			return f'Error during convert<{selfToStr}> to string: {type(ex)} "{ex}"'


@onSignal('actl.NativeFunction:created')
async def _onNativeFunctionCreated(NativeFunction):
	_GetAttributeView.Function = NativeFunction


@onSignal('actl.Function:created')
async def _onFunctionCreated(Function):
	_GetAttributeView.Function = Function


@onSignal('actl.String:created')
async def _onStringCreated(String):
	AObject.String = String
