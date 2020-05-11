class _GenericKeyExceptionMixin:
	MSG = 'Generic Error: {key}'

	def __repr__(self):
		return f'{type(self).__name__}(key={self.key})'

	def __str__(self):
		return self.MSG.format(key=self.key)


class _MetaAGenericKeyError(type, _GenericKeyExceptionMixin):
	MSG = 'Generic Error: {key}'

	def __call__(self, key=None):
		class Temp(self, metaclass=type):
			_key = key

		Temp.__name__ = f'{self.__name__} for {key}'
		return type.__call__(Temp)

	def __repr__(self):
		return f'{type(self).__name__}(key={self._key})'

	def __str__(self):
		return self.MSG.format(key=self._key)


class AGenericKeyError(Exception, metaclass=_MetaAGenericKeyError):
	pass


class AAttributeIsNotSpecial(AGenericKeyError):
	MSG = 'This atribute is not special: {key}'


class AAttributeNotFound(AGenericKeyError):
	MSG = 'This attribute not found: {key}'


class AKeyNotFound(AGenericKeyError):
	MSG = 'This key not found: {key}'
