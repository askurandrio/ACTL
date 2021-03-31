from actl.objects.object.exceptions import AAttributeNotFound, AAttributeIsNotSpecial
from actl.objects.object.AObjectBase import AObjectBase
from actl.objects.object.NativeMethod import NativeMethod


class AObjectClass(AObjectBase):
	Object = None

	def __init__(self, name):
		head = {
			'__name__': name,
			'__self__': {}
		}
		if self.Object is not None:
			head = {
				**head,
				'__parents__': self.Object
			}
		super().__init__(head)

	def _lookupSpecialAttribute(self, key):
		try:
			return self._lookupSpecialAttribute(key)
		except AAttributeIsNotSpecial(key).class_:
			pass

		if key not in '__class__':
			raise AAttributeIsNotSpecial(key)

	def lookupAttribute(self, key):
		try:
			return super().lookupAttribute(key)
		except AAttributeNotFound(key).class_:
			pass

		try:
			return self.super_(None, key)
		except AAttributeNotFound(key).class_:
			pass

	def super_(self, for_, key, bind=True):
		parents = self.getAttribute('__parents__')

		if (for_ is not None) and (for_ in parents):
			parents = parents[parents.index(for_) + 1:]

		for parent in parents:
			try:
				attribute = AObjectBase.lookupAttribute(parent, key)
			except AAttributeNotFound:
				continue
			else:
				if bind:
					return self.bindAttribute(attribute)
				return attribute

