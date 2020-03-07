class SlotsViaGetAttr:
	def __getattr__(self, key):
		raise NotImplementedError

	def __call__(self, *args, **kwargs):
		return self.__getattr__('__call__')(*args, **kwargs)

	def __iter__(self):
		return self.__getattr__('__iter__')()

	def __getitem__(self, key):
		return self.__getattr__('__getitem__')(key)

	def __setitem__(self, key, value):
		self.__getattr__('__setitem__')(key, value)

	def __delitem__(self, key):
		self.__getattr__('__delitem__')(key)

	def __contains__(self, key):
		return self.__getattr__('__contains__')(key)

	def __bool__(self):
		return self.__getattr__('__bool__')()

	def __repr__(self):
		return self.__getattr__('__repr__')()

	def __str__(self):
		return self.__getattr__('__str__')()
