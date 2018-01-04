
import copy
import itertools

from ..Buffer import Buffer


class SyntaxRule:
	def __init__(self, template, func=None, in_context=False):
		self.func = func
		self.in_context = in_context
		self.template = [OneOpcode.create(tmpl) for tmpl in template]

	def match(self, buff):
		elements = Buffer(itertools.zip_longest(itertools.count(), self.template, buff))
		while True:
			idx, tmpl, opcode = next(elements)
			if tmpl is None:
				return idx
			if opcode is None:
				return None 
			elements = Buffer.create((idx, tmpl, opcode)) + elements
			if not tmpl.match(elements):
				return None

	def __call__(self, code, idx_start, matched_code):
		if self.in_context:
			return self.func(code=code, idx_start=idx_start, matched_code=matched_code)
		return self.func(*matched_code)

	@staticmethod
	@Buffer.generator
	def only_opcodes(buff):
		for _, _, opcode in buff:
			yield opcode

	def __repr__(self):
		return f'{type(self).__name__}(func={self.func}, template={self.template})'


class OneOpcode(SyntaxRule):
	def __init__(self, template):
		self.__template = template

	def match(self, buff):
		return self.__template == buff.pop(0)[2]

	@classmethod
	def create(cls, template):
		if isinstance(template, SyntaxRule):
			return template
		return cls(template)

	def __repr__(self):
		return f'{self.__template}'


class Or(SyntaxRule):
	def __init__(self, *templates):
		self.__rules = []
		for template in templates:
			self.__rules.append(SyntaxRule(template))

	def match(self, buff):
		for rule in self.__rules:
			backup = copy.deepcopy(buff)
			result = rule.match(super().only_opcodes(buff))
			if result is None:
				buff.update(backup)
			else:
				return True
		return False

	def __repr__(self):
		return f'{type(self).__name__}({self.__rules})'


class SyntaxRules:
	def __init__(self):
		self.rules = []

	def add(self, *args, in_context=False):
		template, func = args[:-1], args[-1]
		if func is None:
			def decorator(func):
				self.rules.append(SyntaxRule(template, func, in_context))
				return func
			return decorator
		self.rules.append(SyntaxRule(template, func, in_context))

	def __iter__(self):
		return iter(self.rules)

	def __repr__(self):
		return f'SyntaxRules(rules={self.rules})'
