from .SyntaxRule import SyntaxRule


class SyntaxRules:
	def __init__(self, rules=None):
		self._rules = [] if rules is None else rules

	def rawAdd(self, rule):
		self._rules.append(rule)

	def add(self, *template, manual_apply=False, use_parser=False):
		def decorator(func):
			rule = SyntaxRule.wrap(*template, manual_apply=manual_apply, use_parser=use_parser)(func)
			self._rules.append(rule)
			return func
		return decorator

	def __iter__(self):
		return iter(self._rules)

	def __repr__(self):
		return f'{type(self).__name__}(rules={self._rules})'
