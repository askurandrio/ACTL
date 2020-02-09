from actl.objects.object.exceptions import AKeyNotFound, AAttributeNotFound
from actl.objects.object.Super import Super


class SuperSelf(Super):
	def __init__(self, parents, aSelf):
		super().__init__(parents, aSelf)
		self._parents = [parent.getAttr('__self__') for parent in self._parents]

	def findAttr(self, key):
		for parent in self._parents:
			try:
				return parent.getItem(key)
			except AKeyNotFound:
				pass
		raise AAttributeNotFound(key=key)
