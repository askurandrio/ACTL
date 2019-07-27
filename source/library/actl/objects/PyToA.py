from .Object import BuildClass, ANotFoundAttribute


PyToA = BuildClass('PyToA')


@PyToA.addMethod('__call__')
def _(self, *args, **kwargs):
	self._val(*args, **kwargs)


@PyToA.addMethod('__getAttr__')
def _(self, key):
	try:
		return self.getAttr('__super__').getAttr('__getAttr__').call(key)
	except ANotFoundAttribute:
		pass
	val = getattr(self._val, key)
	return PyToA.fromPy(val)


@PyToA.addMethod('__toStr__')
def _(self):
	return self._val.__name__


@PyToA.addFromPy
def _(obj):
	self = PyToA.call()
	self._val = obj
	return self
