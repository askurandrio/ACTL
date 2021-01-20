from functools import lru_cache


class _GenericKeyExceptionMixin:
	def __repr__(self):
		return f'{type(self).__name__}(key={self.key})'

	def __str__(self):
		return self.MSG.format(key=self.key)


class _MetaAGenericKeyError(type, _GenericKeyExceptionMixin):
	_key = None
	MSG = 'Generic Error: {key}'

	def __call__(self, key=None):
		if self._key is None:
			return self._getClassFor(key)(key)

		assert self._key == key
		return super().__call__(key)

	@lru_cache(maxsize=None)
	def _getClassFor(self, key):
		class Temp(self, metaclass=type):
			_key = key

		Temp.__name__ = f'{self.__name__} for {key}'
		return Temp


class AGenericKeyError(Exception, metaclass=_MetaAGenericKeyError):
	pass


class AAttributeIsNotSpecial(AGenericKeyError):
	MSG = 'This atribute is not special: {key}'


class AAttributeNotFound(AGenericKeyError):
	MSG = 'This attribute not found: {key}'


class AKeyNotFound(AGenericKeyError):
	MSG = 'This key not found: {key}'
