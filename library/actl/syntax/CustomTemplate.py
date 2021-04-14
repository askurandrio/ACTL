from functools import lru_cache

from actl.Buffer import Buffer
from actl.syntax.AbstractTemplate import AbstractTemplate
from actl.syntax.NamedResult import NamedResult


class CustomTemplate(AbstractTemplate):
	__slots__ = ('name', 'func')

	def __call__(self, parser, inp):
		return self.func(parser, inp)

	@classmethod
	def asArg(cls, template, arg):
		def asArg(parser, inp):
			res = template(parser, inp)
			if res is None:
				return res
			return Buffer.of(NamedResult(arg, res))

		return CustomTemplate(f'{cls.__name__}.asArg({template}, {arg})', asArg)

	@classmethod
	def create(cls, func, name=None):
		name = func.__name__ if name is None else name
		return cls(name, func)

	@classmethod
	def createToken(cls, func, name=None):
		def template(parser, inp):
			if not inp:
				return None
			token = inp[0]
			if func(parser, token):
				inp.shift()
				return Buffer.of(token)
			return None

		name = func.__name__ if name is None else name
		return cls.create(template, name)

	def __repr__(self):
		return f'{type(self).__name__}({self.name})'


@lru_cache(maxsize=None)
def IsInstance(cls):
	def rule(_, val):
		return isinstance(val, cls)

	return CustomTemplate.createToken(rule, f'IsInstance({cls})')


@CustomTemplate.create
def End(_, buff):
	if buff:
		return None

	return Buffer()
