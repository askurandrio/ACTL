from functools import lru_cache

from actl.Buffer import Buffer
from actl.syntax.AbstractTemplate import AbstractTemplate
from actl.syntax.NamedResult import NamedResult
from actl.syntax.Token import Token


IS_APPLYING_END_DICT = {}


class CustomTemplate(AbstractTemplate):
	__slots__ = ('name', 'func')

	async def __call__(self, parser, inp):
		return await self.func(parser, inp)

	@classmethod
	def asArg(cls, template, arg):
		async def asArg(parser, inp):
			res = await template(parser, inp)
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
		async def template(parser, inp):
			if not inp:
				return None
			token = inp[0]
			if await func(parser, token):
				del inp[0]
				return Buffer.of(token)
			return None

		name = func.__name__ if name is None else name
		return cls.create(template, name)

	def __repr__(self):
		return f'{type(self).__name__}({self.name})'


@lru_cache(maxsize=None)
def IsInstance(cls):
	async def rule(_, val):
		return isinstance(val, cls)

	return CustomTemplate.createToken(rule, f'IsInstance({cls})')


@CustomTemplate.create
async def End(parser, buff):
	if not buff:
		return Buffer()

	if parser in IS_APPLYING_END_DICT:
		return await Token('\n')(parser, buff)

	IS_APPLYING_END_DICT[parser] = True

	try:
		return await parser.endLine(parser, buff)
	finally:
		del IS_APPLYING_END_DICT[parser]
