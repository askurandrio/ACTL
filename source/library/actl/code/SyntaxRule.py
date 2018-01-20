
import copy
import enum
import itertools

from ..Buffer import Buffer


class SyntaxRule:
	def __init__(self, template, func=None, in_context=False):
		self.func = func
		self.in_context = in_context
		self.template = [OneOpcode.create(tmpl) for tmpl in template]

	def match(self, buff):
		template = iter(self.template)
		elements = Buffer(itertools.zip_longest(itertools.count(), template, buff))
		while True:
			idx, tmpl, opcode = next(elements)
			if tmpl is None:
				return idx
			if opcode is None:
				return None 
			elements = Buffer.create((idx, tmpl, opcode)) + elements
			if not tmpl.match(elements):
				return None

	def __call__(self, code, idx_start, idx_end):
		if self.in_context:
			return self.func(code, idx_start, idx_end)
		return self.func(code, *code.buff[idx_start:idx_start+idx_end])

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
		for idx, rule in enumerate(self.__rules):
			backup = copy.deepcopy(buff)
			result = rule.match(super().only_opcodes(buff))
			if result is None:
				if idx == len(self.__rules) - 1:
					return False
				buff.update(backup)
			else:
				return True
		return False

	def __repr__(self):
		return f'{type(self).__name__}({self.__rules})'


class Not(SyntaxRule):
	def __init__(self, not_match, rule):
		self.not_match = SyntaxRule(not_match, None)
		self.rule = SyntaxRule(rule, None)

	def match(self, buff):
		backup = copy.deepcopy(buff)
		result = self.not_match.match(super().only_opcodes(buff))
		if result is None:
			buff.update(backup)
			return self.rule.match(super().only_opcodes(buff))
		return False

	def __repr__(self):
		return f'{type(self).__name__}({self.template})'


class SyntaxRules:
	def __init__(self):
		self.rules = []

	def add(self, *template, in_context=False):
		def decorator(func):
			self.rules.append(SyntaxRule(template, func, in_context))
			return func
		return decorator

	def __iter__(self):
		return iter(self.rules)

	def __repr__(self):
		return f'SyntaxRules(rules={self.rules})'