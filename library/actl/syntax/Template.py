# pylint: disable=no-member

from actl.Buffer import Buffer
from actl.opcodes import VARIABLE
from actl.syntax.NamedResult import NamedResult


class AbstractTemplate:
	__slots__ = ('arg',)

	def __init__(self, *args, **kwargs):
		kwargs.setdefault('arg', None)
		kwargs.update(zip(self.__slots__, args))
		for key, value in kwargs.items():
			setattr(self, key, value)
		for key in self.__slots__:
			assert hasattr(self, key), f'{self} has no attribute {key}'

	def asArg(self, arg):
		def asArg(parser, inp):
			res = self(parser, inp)
			if res is None:
				return res
			return Buffer.of(NamedResult(arg, res))

		return CustomTemplate(f'{self}.asArg({arg})', asArg)

	def __call__(self, parser, inp):
		raise NotImplementedError

	def __repr__(self):
		args = ', '.join(str(getattr(self, key)) for key in self.__slots__)
		return f'{type(self).__name__}({args})'


class _MetaTemplate(type(AbstractTemplate)):
	def __call__(self, *template):
		if (len(template) == 1) and isinstance(template[0], AbstractTemplate):
			return template[0]
		return super().__call__(*template)


class Template(AbstractTemplate, metaclass=_MetaTemplate):
	__slots__ = ('_template',)

	def __init__(self, *template):
		super().__init__(template)

	def __call__(self, parser, buff):
		with buff.transaction() as tx:
			res = Buffer()
			for tmpl in self._template:
				tmpl_res = tmpl(parser, buff)
				if tmpl_res is None:
					return None
				res += tmpl_res
			tx.commit()
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
			token = inp[0]
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
		with inp.transaction() as mainTx:
			for matches in Buffer.inf():
				with inp.transaction() as iterationTx:
					tmpl_res = self.template(parser, inp)
					if tmpl_res is None:
						if matches < self.min_matches:
							return None

						mainTx.commit()
						return res

					iterationTx.commit()

				res += tmpl_res

		raise RuntimeError('Unexpected branch')


class Or(AbstractTemplate):
	__slots__ = ('templates',)

	def __init__(self, *templates):
		templates = tuple(Template(*template) for template in templates)
		super().__init__(templates)

	def __call__(self, parser, inp):
		for template in self.templates:
			with inp.transaction() as tx:
				res = template(parser, inp)
				if res is not None:
					tx.commit()
					return res
		return None


class Maybe(AbstractTemplate):
	__slots__ = ('template',)

	def __init__(self, *template):
		super().__init__(Template(*template))

	def __call__(self, parser, inp):
		with inp.transaction() as tx:
			res = self.template(parser, inp)
			if res is not None:
				tx.commit()
				return res
		return Buffer()


class Value(AbstractTemplate):
	__slots__ = ('value',)

	def __call__(self, parser, buff):
		if (not buff) or (VARIABLE != buff[0]) or (parser.scope.get(buff[0].name) != self.value):
			return None

		return Buffer.of(buff.pop(0))


class Frame(AbstractTemplate):
	__slots__ = ('until',)

	def __init__(self, *templates):
		super().__init__(Template(*templates))

	def __call__(self, parser, buff):
		res = parser.subParser(buff, self.until).parseLine()
		return tuple(res)


def Token(token):
	def rule(_, val):
		return token == val

	return CustomTemplate.createToken(rule, f'Token({token})')


def IsInstance(cls):
	def rule(_, val):
		return isinstance(val, cls)

	return CustomTemplate.createToken(rule, f'IsInstance({cls})')


@CustomTemplate.create
def BreakPoint(_, _1):
	breakpoint()
	return Buffer()


@CustomTemplate.create
def End(_, buff):
	if buff:
		return None

	return Buffer()
