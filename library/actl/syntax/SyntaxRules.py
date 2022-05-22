from .SyntaxRule import SyntaxRule


class SyntaxRules:
	def __init__(self, from_=None):
		if from_ is None:
			rules = []
		else:
			rules = list(from_)

		self._rules = rules

	def match(self, parser, buff):
		for rule in self._rules:
			apply = rule.match(parser, buff)
			if apply:
				return apply
		return None

	def rawAdd(self, rule):
		self._rules.append(rule)

	def add(self, *template, manualApply=False, useParser=False):
		def decorator(func):
			rule = SyntaxRule.wrap(
				*template, manualApply=manualApply, useParser=useParser
			)(func)

			self.rawAdd(rule)
			return func

		return decorator

	def __iter__(self):
		return iter(self._rules)

	def __repr__(self):
		return f'{type(self).__name__}(rules=...)'
