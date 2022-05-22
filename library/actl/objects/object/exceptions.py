class _GenericKeyExceptionMixin:
	def __repr__(self):
		return f'{type(self).__name__}(key={self.key})'

	def __str__(self):
		return self.MSG.format(key=self.key)


class _MetaAGenericKeyError(type, _GenericKeyExceptionMixin):
	MSG = 'Generic Error: {key}'

	def __call__(self, key=''):
		if key == '':
			instance = super().__call__(key)
			return instance

		cls = self.class_(key=key)
		return cls('')


class AGenericKeyError(Exception, _GenericKeyExceptionMixin, metaclass=_MetaAGenericKeyError):
	_GCACHE = {}

	@classmethod
	def class_(cls, key):
		clsKey = cls, key

		if clsKey in cls._GCACHE:
			return cls._GCACHE[clsKey]

		cls._GCACHE[clsKey] = type(f'{cls.__name__} for {key}', (cls,), {'key': key})
		return cls.class_(key)

	@classmethod
	def check(cls, isSucess, *args, **kwargs):
		if isSucess:
			return

		raise cls(*args, **kwargs)


class AAttributeIsNotSpecial(AGenericKeyError):
	MSG = 'This atribute is not special: {key}'


class AAttributeNotFound(AGenericKeyError):
	MSG = 'This attribute not found: {key}'


class AKeyNotFound(AGenericKeyError):
	MSG = 'This key not found: {key}'
