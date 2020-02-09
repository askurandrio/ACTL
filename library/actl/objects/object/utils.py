from actl.objects.object.exceptions import AAttributeNotFound


def loadPropIfNeed(self, val):
	try:
		prop = val.get
	except (AAttributeNotFound, AttributeError):
		return val
	else:
		return prop(self)
