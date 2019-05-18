import pdb

from actl import Buffer


class Template:
	def __init__(self, *template):
		self._template = template

	def __call__(self, buff):
		res = Buffer()
		for tmpl in self._template:
			tmpl_res = tmpl(buff)
			if tmpl_res is None:
				return None
			res += tmpl_res
		return res

	def __repr__(self):
		return f'{type(self).__name__}({self._template})'


def Pdb():
	def rule(buff):
		pdb.set_trace()
		return Buffer()
	return rule


class Rule:
	def __init__(self, *args, **kwargs):
		kwargs.update(zip(self.__slots__, args))
		for key, value in kwargs.items():
			setattr(self, key, value)
		for key in self.__slots__:
			assert hasattr(self, key), f'{self} has no attribute {key}'
	
	def __repr__(self):
		args = ', '.join(str(getattr(self, key)) for key in self.__slots__)
		return f'{type(self).__name__}({args})'


class CustomRule(Rule):
	__slots__ = ('name', 'func')
	
	def __call__(self, buff):
		try:
			token = buff.pop()
		except IndexError:
			return None
		if self.func(token):
			return Buffer([token])
		return None

	def __repr__(self):
		return f'{type(self).__name__}({self.name})'


class SimpleToken(Rule):
	__slots__ = ('token',)
	
	def __call__(self, buff):
		try:
			val = buff.pop()
		except IndexError:
			return None
		if self.token == val:
			return Buffer([val])
		return None
	

class IsInstance(Rule):
	__slots__ = ('cls',)
	
	def __call__(self, buff):
		try:
			token = buff.pop()
		except IndexError:
			return None
		if isinstance(token, self.cls):
			return Buffer([token])
		return None


class Many(Rule):
	__slots__ = ('template', 'min_matches')
	
	def __init__(self, *template, min_matches=1):
		super().__init__(Template(*template), min_matches)
		
	def __call__(self, buff):
		matches = 0
		res = Buffer()
		while True:
			tmpl_res = self.template(buff)
			if tmpl_res is None:
				if matches < self.min_matches:
					return None
				return res
			res += tmpl_res


class Or(Rule):
	__slots__ = ('templates',)
	
	def __init__(self, *templates):
		super().__init__(templates)
	
	def __call__(self, buff):
		inp = buff
		for template in self.templates:
			buff = inp.copy()
			template = Template(*template)
			res = template(buff)
			if res:
				inp.set(buff)
				return res
		return None
