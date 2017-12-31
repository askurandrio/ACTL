
import itertools


class SyntaxRule:
	def __init__(self, func, template):
		self.func = func
		self.template = template
		self.add_context = False

	def match(self, buff):
		for idx, tmpl, data in itertools.zip_longest(itertools.count(), self.template, buff):
			if tmpl is None:
				return idx - 1
			elif data is None:
				return None
			elif tmpl != data:
				return None

	def __call__(self, code, idx_start, matched_code):
		if self.add_context:
			context = {'code':code, 'idx_start':idx_start}
			return self.func(context=context, *matched_code)
		else:
			return self.func(*matched_code)

	def __repr__(self):
		return f'SyntaxRule(func={self.func}, template={self.template}'

class SyntaxRules:
	def __init__(self):
		self.rules = []

	def add(self, template, func):
		if func is not None:
			self.rules.append(SyntaxRule(func, template))
		def decorator(func):
			if func is None:
				self.rules.append(SyntaxRule(func, template))
			return func
		return decorator

	def __iter__(self):
		return iter(self.rules)

	def __repr__(self):
		return f'SyntaxRules(rules={self.rules})'
