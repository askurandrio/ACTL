
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
