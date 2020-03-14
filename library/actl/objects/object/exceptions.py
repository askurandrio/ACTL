class AGenericKeyError(Exception):
	MSG = 'Generic Error: {key}'

	def __init__(self, key=None):
		self.key = key
		super().__init__(self.MSG.format(key=self.key))

	def check(self, key):
		if self.key != key:
			raise self


class AAttributeIsNotSpecial(AGenericKeyError):
	MSG = 'This atribute is not special: {key}'


class AAttributeNotFound(AGenericKeyError):
	MSG = 'This attribute not found: {key}'


class AKeyNotFound(AGenericKeyError):
	MSG = 'This key not found: {key}'
