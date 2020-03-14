from actl.objects.object.utils import loadPropIfNeed
from actl.objects.object.exceptions import AAttributeNotFound, AKeyNotFound
from actl.objects.object.AbstractObject import AbstractObject


class InstanceObject(AbstractObject):
	def super_(self, for_, key, bind=True):
		parents = self.class_.parents
		if for_ in parents:
			parents = parents[parents.index(for_) + 1:]
		for parent in parents:
			try:
				prop = parent.getAttr('__self__').getItem(key)
			except AKeyNotFound as ex:
				ex.check(key)
				continue
			if bind:
				prop = loadPropIfNeed(self, prop)
			return prop
		raise AAttributeNotFound(key)

	def findAttr(self, key):
		try:
			return self._head[key]
		except KeyError:
			ex = AAttributeNotFound(key=key)
		self_ = self.class_.getAttr('__self__')
		try:
			return self_.getItem(key)
		except AKeyNotFound:
			pass
		try:
			return self.super_(self.class_, key, bind=False)
		except AAttributeNotFound as superEx:
			superEx.check(key)
			raise ex
