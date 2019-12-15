from .Object import BuildClass


String = BuildClass('String')


@String.addMethodToClass('__init__')
def _(cls, value=''):
	self = cls.getAttr('__super__').getAttr('__init__').call()
	self._val = value
	return self


@String.addFromPy
def _(cls, value):
	return cls.call(value)
