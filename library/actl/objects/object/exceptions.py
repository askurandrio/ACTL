class AGenericKeyError(Exception):
	MSG = 'Generic Error: {key}'

	def __init__(self, msg='', key=None):
		if (key is not None) and (not msg):
			msg = self.MSG.format(key=key)
		super().__init__(msg)


class AAttributeIsNotSpecial(AGenericKeyError):
	MSG = 'This atribute is not special: {key}'


class AAttributeNotFound(AGenericKeyError):
	MSG = 'This attribute not found: {key}'


class AKeyNotFound(AGenericKeyError):
	MSG = 'This key not found: {key}'
