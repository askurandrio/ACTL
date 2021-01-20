from actl.objects.object.exceptions import AAttributeNotFound


def loadPropIfNeed(self, val):
	try:
		prop = val.get
	except (AAttributeNotFound, AttributeError):
		return val
	else:
		try:
			return prop(self)
		except:
			breakpoint()
