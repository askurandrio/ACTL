from .Object import BuildClass


PyToA = BuildClass('PyToA')


@PyToA.addMethod('__call__')
def _(self, *args, **kwargs):
	return self._val(*args, **kwargs)


@PyToA.addMethod('__getattr__')
def _(self, *args, **kwargs):
	print('getattr')


@PyToA.addMethod('__toStr__')
def _(self):
	return self._val.__name__


@PyToA.addFromPy
def _(obj):
	self = PyToA.call()
	self._val = obj
	return self
