
import copy
import itertools

from ..Buffer import Buffer


class SyntaxRule:
	def __init__(self, template, func):
		self.func = func
		self.template = [SearchTemplate.create(tmpl) for tmpl in template]
		self.add_context = False

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
		if self.add_context:
			context = {'code':code, 'idx_start':idx_start}
			return self.func(context=context, *matched_code)
		else:
			return self.func(*matched_code)

	@staticmethod
	@Buffer.generator
	def only_opcodes(buff):
		for _, _, opcode in buff:
			yield opcode

	def __repr__(self):
		return f'{type(self).__name__}(func={self.func}, template={self.template}'


class SearchTemplate:
	def __init__(self, template):
		self.__template = template

	def match(self, buff):
		return self.__template == buff.pop(0)[2]

	@classmethod
	def create(cls, template):
		if isinstance(template, cls):
			return template
		return cls(template)

	def __repr__(self):
		return f'{type(self).__name__}(template={self.__template})'


class Maybe(SyntaxRule, SearchTemplate):
	def __init__(self, *template):
		super().__init__(func=None, template=template)

	def match(self, buff):
		backup = copy.deepcopy(buff)
		result = super().match(super().only_opcodes(buff))
		if result is None:
			buff.update(backup)
		return False


class Many(SyntaxRule, SearchTemplate):
	def __init__(self, *template):
		super().__init__(func=None, template=template)

	def match(self, buff):
		is_find = False
		while True:
			backup = copy.deepcopy(buff)
			result = super().match(super().only_opcodes(buff))
			print(self, super().only_opcodes(buff.__deepcopy__()), result, sep=' || ')
			if result is None:
				buff.update(backup)
				return is_find
			else:
				is_find = True
				buff.update(backup[result:])


class SyntaxRules:
	def __init__(self):
		self.rules = []

	def add(self, *args):
		template, func = args[:-1], args[-1]
		if func is None:
			def decorator(func):
				if func is None:
					self.rules.append(SyntaxRule(template, func))
				return func
			return decorator
		self.rules.append(SyntaxRule(template, func))

	def __iter__(self):
		return iter(self.rules)

	def __repr__(self):
		return f'SyntaxRules(rules={self.rules})'
