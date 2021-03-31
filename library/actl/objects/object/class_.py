from actl.objects.object.AObject import AObject
from actl.objects.object.NativeMethod import NativeMethod
from actl.objects.object.exceptions import AAttributeIsNotSpecial, AAttributeNotFound


def class__getAttribute(self, key):
	try:
		return self.lookupSpecialAttribute(key)
	except AAttributeIsNotSpecial(key).class_:
		pass

	try:
		attribute = self.lookupAttributeInHead(key)
	except AAttributeNotFound(key).class_:
		pass
	else:
		return self.bindAttribute(attribute)

	try:
		attribute = self.lookupAttributeInClsSelf(key)
	except AAttributeNotFound(key).class_:
		pass
	else:
		return self.bindAttribute(attribute)

	raise AAttributeNotFound(key)


class_ = AObject({
	'__name__': 'class',
	'__parents__': (),
	'__self__': {
		'__getAttribute__': NativeMethod(class__getAttribute)
	}
})
