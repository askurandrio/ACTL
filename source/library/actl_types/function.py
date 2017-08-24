from actl_types import actl_object


class Function(actl_object):
	def __init__(self, name='', code=None):
		self.name = name
		self.code = code
