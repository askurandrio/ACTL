from contextlib import contextmanager

from .SyntaxRule import SyntaxRule


class SyntaxRules:
	def __init__(self, from_=None):
		if from_ is None:
			rules = []
		else:
			rules = list(from_)

		self._rules = rules

	@contextmanager
	def disable(self, *rules):
		def lookup(key):
			if isinstance(key, SyntaxRule):
				return key

			for rule in self._rules:
				if isinstance(rule, SyntaxRule) and rule.func.__name__ == key:
					return rule

			return None

		rules = [lookup(rule) for rule in rules]
		indexes = []

		for rule in rules:
			if rule in self._rules:
				index = self._rules.index(rule)
			else:
				index = None
			indexes.append(index)
			if index is not None:
				del self._rules[index]

		yield

		for index, rule in reversed(tuple(zip(indexes, rules))):
			if index is None:
				continue
			self._rules.insert(index, rule)

	async def match(self, parser, buff):
		for rule in self._rules:
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
