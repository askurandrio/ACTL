from .Object import BuildClass


String = BuildClass('String')
_default = object()


@String.addMethodToClass('__init__')
def _(cls, value=_default):
	self = cls.getAttr('__super__').getAttr('__init__').call()
	if value is _default:
		self._val = ''
	else:
		self._val = value
	return self


@String.addFromPy
def _(cls, value):
	return cls.call(value)
