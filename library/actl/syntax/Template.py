import pdb

from actl.Buffer import Buffer
from actl.opcodes import VARIABLE


class AbstractTemplate:
	__slots__ = ()

	def __init__(self, *args, **kwargs):
		kwargs.update(zip(self.__slots__, args))
		for key, value in kwargs.items():
			setattr(self, key, value)
		for key in self.__slots__:
			assert hasattr(self, key), f'{self} has no attribute {key}'

	def __repr__(self):
		args = ', '.join(str(getattr(self, key)) for key in self.__slots__)
		return f'{type(self).__name__}({args})'


class Template(AbstractTemplate):
	__slots__ = ('_template',)

	def __init__(self, *template):
		super().__init__(template)

	def __call__(self, parser, buff):
		backup = buff.copy()
		res = Buffer()
		for tmpl in self._template:
			tmpl_res = tmpl(parser, buff)
			if tmpl_res is None:
				buff.set_(backup)
				return None
			res += tmpl_res
		return res

	def __repr__(self):
		repr_template = ', '.join(str(tmpl) for tmpl in self._template)
		return f'{type(self).__name__}({repr_template})'


class CustomTemplate(AbstractTemplate):
	__slots__ = ('name', 'func')

	def __call__(self, parser, inp):
		return self.func(parser, inp)

	@classmethod
	def create(cls, func, name=None):
		name = func.__name__ if name is None else name
		return cls(name, func)

	@classmethod
	def createToken(cls, func, name=None):
		def template(parser, inp):
			if not inp:
				return None
			token = inp.get(0)
			if func(parser, token):
				inp.pop(0)
				return Buffer.of(token)
			return None

		name = func.__name__ if name is None else name
		return cls.create(template, name)

	def __repr__(self):
		return f'{type(self).__name__}({self.name})'


class Many(AbstractTemplate):
	__slots__ = ('template', 'min_matches')

	def __init__(self, *template, min_matches=1):
		assert min_matches != 0, f'min_matched<{min_matches}> == 0. Use Maybe for this case'
		super().__init__(Template(*template), min_matches)

	def __call__(self, parser, inp):
		res = Buffer()
		for matches in Buffer.inf():
			buff = inp.copy()
			tmpl_res = self.template(parser, buff)
			if tmpl_res is None:
				if matches < self.min_matches:
					return None
				return res
			inp[:] = buff
			res += tmpl_res


class Or(AbstractTemplate):
	__slots__ = ('templates',)

	def __init__(self, *templates):
		super().__init__(templates)

	def __call__(self, parser, inp):
		for template in self.templates:
			buff = inp.copy()
			template = Template(*template)
			res = template(parser, buff)
			if res is not None:
				inp[:] = buff
				return res
		return None


class Maybe(AbstractTemplate):
	__slots__ = ('template',)

	def __init__(self, *template):
		super().__init__(Template(*template))

	def __call__(self, parser, buff):
		inp = buff.copy()
		res = self.template(parser, inp)
		if res is not None:
			buff[:] = inp
			return res
		return Buffer()


class Value(AbstractTemplate):
	__slots__ = ('value',)

	def __call__(self, parser, buff):
		if (VARIABLE != buff[0]) or (parser.scope.get(buff[0].name) != self.value):
			return None

		return Buffer.of(buff.pop(0))


def Token(token):
	def rule(_, val):
		return token == val

	return CustomTemplate.createToken(rule, f'Token({token})')


def IsInstance(cls):
	def rule(_, val):
		return isinstance(val, cls)

	return CustomTemplate.createToken(rule, f'IsInstance({cls})')


@CustomTemplate.create
def pdb(_, _1):
	pdb.set_trace()
	return Buffer()


@CustomTemplate.create
def End(_, buff):
	if buff:
		return None

	return Buffer()


@CustomTemplate.create
def Frame(parser, buff):
	assert buff
	res, newBuff = parser.subParse(buff)
	buff.set_(newBuff)
	return res
