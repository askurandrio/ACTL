class AGenericKeyError(Exception):
	MSG = 'Generic Error: {key}'

	def __init__(self, key=None):
		self.key = key
		super().__init__()

	def check(self, key):
		if self.key != key:
			raise self

	def __repr__(self):
		return f'{type(self).__name__}(key={self.key})'

	def __str__(self):
		return self.MSG.format(key=self.key)


class AAttributeIsNotSpecial(AGenericKeyError):
	MSG = 'This atribute is not special: {key}'


class AAttributeNotFound(AGenericKeyError):
	MSG = 'This attribute not found: {key}'


class AKeyNotFound(AGenericKeyError):
	MSG = 'This key not found: {key}'
