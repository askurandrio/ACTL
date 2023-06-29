from contextlib import contextmanager

from .SyntaxRule import SyntaxRule


class SyntaxRules:
	def __init__(self, from_=None):
		if from_ is None:
			rules = []
		else:
			rules = list(from_)

		self._rules = rules
		self._disabled = []

	@contextmanager
	def disable(self, *keys):
		self._disabled.extend(keys)

		yield

		for key in keys:
			self._disabled.remove(key)

	def isDisabled(self, rule):
		for key in self._disabled:
			if rule == key:
				return True

			if isinstance(rule, SyntaxRule) and rule.func.__name__ == key:
				return True

		return False

	async def match(self, parser, buff):
		for rule in self._rules:
			if self.isDisabled(rule):
				continue

			apply = await rule.match(parser, buff)
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
			return rule

		return decorator

	def __iter__(self):
		return iter(self._rules)

	def __repr__(self):
		return f'{type(self).__name__}(rules=...)'
