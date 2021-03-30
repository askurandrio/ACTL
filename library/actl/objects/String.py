# pylint: disable=protected-access
from actl.objects.object import BuildClass


class _BuildClassString(BuildClass):
	def __str__(self):
		name = self.getAttribute('__name__')
		return f"class '{name}'"


String = _BuildClassString('String')


@String.addMethodToClass('__call__')
def _(cls, value=''):
	self = cls.super_(String, '__call__').call()
	self._value = value
	return self
