from contextlib import contextmanager


@contextmanager
def setAttrForBlock(obj, attr, value):
	# pylint: disable=unexpected-special-method-signature, invalid-overridden-method
	prevValue = getattr(obj, attr)
	setattr(obj, attr, value)
	yield
	setattr(obj, attr, prevValue)
