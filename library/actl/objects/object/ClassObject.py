from actl.objects.object.exceptions import AAttributeNotFound
from actl.objects.object.utils import loadPropIfNeed
from actl.objects.object.AbstractObject import AbstractObject


class ClassObject(AbstractObject):
	_specialAttrs = {
		**AbstractObject._specialAttrs,
		'__parents__': 'parents',
		'__self__': '__self__'
	}

	@property
	def parents(self):
		return self._head['__parents__']

	@property
	def __self__(self):
		return self._head['__self__']

	def super_(self, for_, key, bind=True):
		parents = self.parents
		if for_ in parents:
			parents = parents[parents.index(for_) + 1:]
		for parent in parents:
			try:
				prop = parent.findAttr(key)
			except AAttributeNotFound:
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
		try:
			return self.super_(self, key, bind=False)
		except AAttributeNotFound:
			raise ex
