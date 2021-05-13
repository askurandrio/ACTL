from actl.objects.object.Result import Result
from actl.objects.object.AObject import AObject
from actl.objects.object.NativeMethod import NativeFunction, NativeMethod
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

	for parent in self.parents:
		try:
			attribute = parent.lookupAttributeInHead(key)
		except AAttributeNotFound(key).class_:
			pass
		else:
			return self.bindAttribute(attribute)

	raise AAttributeNotFound(key)


def class__superGetAttribute(self, for_, key):
	parents = self.getAttribute('__parents__')

	if for_ in parents:
		forIndex = parents.index(for_)
		parents = parents[forIndex+1:]

	for parent in parents:
		try:
			attribute = parent.lookupAttributeInHead(key)
		except AAttributeNotFound(key).class_:
			pass
		else:
			return self.bindAttribute(attribute)

	raise AAttributeNotFound(key)


class_ = AObject({
	'__name__': 'class',
	'__parents__': (),
	'__self__': {
		'__getAttribute__': NativeMethod(class__getAttribute),
		'__superGetAttribute__': NativeMethod(class__superGetAttribute)
	}
})
class_.setAttribute('__class__', class_)
class_.setAttribute('__getAttribute__', NativeFunction(class__getAttribute).apply(class_))
