from actl.objects.object.NativeFunc import NativeFunc
from actl.objects.object.utils import loadPropIfNeed
from actl.objects.object.exceptions import AAttributeNotFound
from actl.objects.object.NativeProperty import NativeProperty
from actl.objects.object.NativeClass import NativeClass


class Super(NativeClass):
	def __init__(self, parents, aSelf):
		super().__init__()
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

	@classmethod
	def make(cls, parents):
		@NativeFunc.wrap(f'fget_{cls.__name__}')
		def fget(aSelf):
			return cls(parents, aSelf)
		return NativeProperty(fget)

	def __str__(self):
		return f'{type(self).__name__}<{self._parents}>'
