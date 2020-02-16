from actl.objects.object import Object, loadPropIfNeed, AAttributeNotFound, nativeProperty, \
	nativeFunc


class _MetaSuper(type):
	def __call__(self, parents):
		@nativeFunc(f'fget_{self.__name__}')
		def fget(aSelf):
			return type.__call__(self, parents, aSelf)

		return nativeProperty(fget)


class Super(type(Object), metaclass=_MetaSuper):
	def __init__(self, parents, aSelf):
		super().__init__({})
		self._parents = parents
		self._aSelf = aSelf

	def findAttr(self, key):
		for parent in self._parents:
			try:
				return parent.findAttr(key)
			except AAttributeNotFound:
				pass
		raise AAttributeNotFound(key=key)

	def getAttr(self, key):
		return loadPropIfNeed(self._aSelf, self.findAttr(key))

	def __str__(self):
		return f'{type(self).__name__}<{self._parents}>'
