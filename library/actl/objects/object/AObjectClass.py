from actl.objects.object.exceptions import AAttributeNotFound, AAttributeIsNotSpecial
from actl.objects.object.AObjectBase import AObjectBase


class AObjectClass(AObjectBase):
	def _lookupSpecialAttribute(self, key):
		try:
			return super()._lookupSpecialAttribute(key)
		except AAttributeIsNotSpecial(key).class_:
			pass
		if key in ('__self__', '__parents__'):
			return super().lookupAttribute(key)
		raise AAttributeIsNotSpecial(key)

	def lookupAttribute(self, key):
		try:
			attribute = super().lookupAttribute(key)
		except AAttributeNotFound(key).class_:
			pass
		else:
			return self.bindProperty(attribute)

		try:
			return self.super_(None, key, bindTo=self)
		except AAttributeNotFound(key).class_:
			pass

	def lookupAttributeInSelf(self, key, bindTo=None):
		if bindTo is None:
			bindTo = self

		classSelf = self.getAttribute('__self__')
		try:
			attribute = classSelf[key]
		except KeyError as ex:
			raise AAttributeNotFound(key) from ex

		return bindTo.bindProperty(attribute)

	def super_(self, for_, key, bindTo=None):
		if bindTo is None:
			bindTo = self

		parents = self.getAttribute('__parents__')

		if (for_ is not None) and (for_ in parents):
			parents = parents[parents.index(for_) + 1:]

		for parent in parents:
			try:
				attribute = parent.lookupAttribute(key)
			except AAttributeNotFound:
				continue
			return bindTo.bindProperty(attribute)

		return super().super_(for_, key, bindTo)
