from .Object import BuildClass, ANotFoundAttribute


PyToA = BuildClass('PyToA')


@PyToA.addMethodToClass('__init__')
def _(cls, value):
	self = cls.getAttr('__super__').getAttr('__init__').call()
	self._value = value
	return self


@PyToA.addMethod('__call__')
def _(self, *args):
	args = (arg._val for arg in args)
	self._value(*args)


@PyToA.addMethod('__getAttr__')
def _(self, key):
	try:
		return self.getAttr('__super__').getAttr('__getAttr__').call(key)
	except ANotFoundAttribute:
		pass
	try:
		value = getattr(self._value, key)
	except AttributeError as ex:
		raise ANotFoundAttribute(ex)
	return PyToA.fromPy(value)


@PyToA.addMethod('__toStr__')
def _(self):
	return self._val.__name__


@PyToA.addFromPy
def _(cls, obj):
	return cls.call(obj)
