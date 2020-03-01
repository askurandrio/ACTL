from .SyntaxRule import SyntaxRule


class SyntaxRules:
	def __init__(self, rules=None):
		self._rules = [] if rules is None else rules

	def rawAdd(self, rule):
		self._rules.append(rule)

	def add(self, *template, manualApply=False, useParser=False):
		def decorator(func):
			rule = SyntaxRule.wrap(*template, manualApply=manualApply, useParser=useParser)(func)
			self.rawAdd(rule)
			return func
		return decorator

	def find(self, name):
		for rule in self._rules:
			if rule.__name__ == name:
				return rule

		raise RuntimeError(f'Rule with such name not found: {name}')

	def __iter__(self):
		return iter(self._rules)

	def __repr__(self):
		return f'{type(self).__name__}(rules={self._rules})'
