class AGenericKeyError(Exception):
	MSG = 'Generic Error: {key}'

	def __init__(self, msg='', key=None):
		if (key is not None) and (not msg):
			msg = self.MSG.format(key=key)
		super().__init__(msg)


class AAttributeNotFound(AGenericKeyError):
	MSG = 'This attribute not found: {key}'


class AKeyNotFound(AGenericKeyError):
	MSG = 'This key not found: {key}'
