from functools import lru_cache


class _GenericKeyExceptionMixin:
	def __repr__(self):
		return f'{type(self).__name__}(key={self.key})'

	def __str__(self):
		return self.MSG.format(key=self.key)


_default = object()


class _MetaAGenericKeyError(type, _GenericKeyExceptionMixin):
	_key = _default
	MSG = 'Generic Error: {key}'

	def __call__(self, key=_default):
		if self._key is _default:
			return self._getClassFor(key=key)('')

		assert key == '', key
		instance = super().__call__(key)
		instance.class_ = self
		return instance

	@lru_cache(maxsize=None)
	def _getClassFor(self, key):
		cls = type(f'{self.__name__} for {key}', (self,), {'_key': key})
		return cls


class AGenericKeyError(Exception, metaclass=_MetaAGenericKeyError):
	pass


class AAttributeIsNotSpecial(AGenericKeyError):
	MSG = 'This atribute is not special: {key}'


class AAttributeNotFound(AGenericKeyError):
	MSG = 'This attribute not found: {key}'


class AKeyNotFound(AGenericKeyError):
	MSG = 'This key not found: {key}'
