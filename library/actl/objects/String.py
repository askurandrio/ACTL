from .Object import BuildClass


String = BuildClass('String')


@String.addMethodToClass('__init__')
def _(cls):
	self = cls.getAttr('__super__').getAttr('__init__').call()
	self._val = ''
	return self


@String.addFromPy
def _(val=''):
	val = str(val)
	string = String.call()
	string._val = val
	return string
