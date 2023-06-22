import inspect


default = object()


def setFunctionName(function, name):
	lc_scope = {'function': function}

	exec(f'def {name}(*args, **kwargs):\n	return function(*args, **kwargs)', lc_scope)

	return lc_scope[name]


def asDecorator(func):
	def decorator(functionForDecorate):
		return func(functionForDecorate)

	return decorator


class DeclaredClass:
	__slots__ = ()
	_defaults = {}

	def __init__(self, *args, **kwargs):
		for idx, value in enumerate(args):
			if self.__slots__[idx] in self._defaults:
				raise RecursionError(
					f'Attribute<{self.__slots__[idx]}> should be named parameter'
				)
			setattr(self, self.__slots__[idx], value)

		for name, value in kwargs.items():
			assert not hasattr(
				self, name
			), f'Attribute<{name}> already declared as {getattr(self, name)}'
			setattr(self, name, value)

		for name, valueFactory in self._defaults.items():
			if hasattr(self, name):
				continue
			setattr(self, name, valueFactory())

		for name in self.__slots__:
			assert hasattr(self, name), f'Attribute<{name}> should be declared'

	def _getAttributes(self):
		return {key: getattr(self, key) for key in self.__slots__}

	def __hash__(self):
		return hash(str(self))

	def __eq__(self, other):
		if type(self) != type(other):  # pylint: disable=unidiomatic-typecheck
			return False
		return self._getAttributes() == other._getAttributes()

	def __repr__(self):
		attributes = self._getAttributes()
		attributesToStr = ', '.join(
			repr(attributes[key]) for key in self.__slots__ if key not in self._defaults
		)
		notDefaultAttributesToStr = ', '.join(
			f'{key}={attributes[key]!r}'
			for key, value in self._defaults.items()
			if value != attributes[key]
		)
		if notDefaultAttributesToStr:
			attributesToStr += f', {notDefaultAttributesToStr}'
		return f'{type(self).__name__}({attributesToStr})'

	@classmethod
	def create(cls, name, *attributes, **defaults):
		attributes = cls.__slots__ + attributes + tuple(defaults)
		defaults = {
			**cls._defaults,
			**{key: (lambda value=value: value) for key, value in defaults.items()},
		}
		class_ = type(name, (cls,), {'__slots__': attributes, '_defaults': defaults})
		return class_


class ReprToStr:
	def __repr__(self):
		return str(self)


def executeSyncCoroutine(coroutine):
	generator = coroutine.__await__()

	try:
		opcode = next(generator)
	except StopIteration as ex:
		if ex.args:
			return ex.args[0]
		return None
	else:
		raise RuntimeError(
			f'Generator do not stopped. Info<opcode={opcode}, coroutine={coroutine}>'
		)


def getEternalIdx():
	frame = inspect.currentframe().f_back
	codePlaceId = frame.f_code.co_filename, frame.f_lineno

	if codePlaceId not in getEternalIdx.store:
		getEternalIdx.store[codePlaceId] = -1

	def incr():
		getEternalIdx.store[codePlaceId] += 1
		return getEternalIdx.store[codePlaceId]

	def decr():
		getEternalIdx.store[codePlaceId] -= 1
		return getEternalIdx.store[codePlaceId]

	return incr, decr


def bindEternalIdx():
	incr, _ = getEternalIdx()
	return incr()


getEternalIdx.store = {}


class Inside:
	def __init__(self):
		self.stack = 0

	def indent(self):
		return self.stack * '    '

	def __enter__(self):
		self.stack += 1

	def __exit__(self, *_):
		self.stack -= 1
