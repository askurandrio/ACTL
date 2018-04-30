
from .Template import Template


class SyntaxRule(Template):
	def __init__(self, template, name, func, in_context=False):
		self.name = name
		self.__func = func
		self.in_context = in_context
		super().__init__(*template)

	def __prepare_arguments(self, args, scope, buff):
		for key in args:
			if key == 'scope':
				yield scope
			elif key == 'rule':
				yield self
			elif key == 'buff':
				yield buff
			else:
				raise RuntimeError(f'This key not found: {key}, rule: {self}')

	def __call__(self, scope, buff):
		if hasattr(self.__func, 'args'):
			args = self.__func.args
		elif self.in_context:
			args = ('scope', 'buff')
		else:
			args = ('buff',)

		args = self.__prepare_arguments(args, scope, buff)
		return self.__func(*args)

	def __repr__(self):
		return super().__repr__()[:-1] + f', {self.__func}, {self.in_context})'


class SyntaxRules:
	def __init__(self):
		self.rules = []

	def add(self, *template, name=None, in_context=False, args=None):
		def decorator(func):
			if args is not None:
				setattr(func, 'args', args)
			self.rules.append(SyntaxRule(template, name, func, in_context))
			return func
		return decorator

	def __iter__(self):
		return iter(self.rules)

	def __repr__(self):
		return f'SyntaxRules(rules={self.rules})'


class Command:
	def __init__(self, command, *args):
		self.command = command
		self.args = args

	def __eq__(self, command):
		return self.command == command.command

	def __repr__(self):
		return f'{type(self).__name__}("{self.command}", *{args})'
