import actl


class Parser(actl.Parser):
	def __init__(self, *args, **kwargs):
		self.applyingRule = False
		super().__init__(*args, **kwargs)

	def _applyRule(self):
		prevApplyingRule, self.applyingRule = self.applyingRule, True
		res = super()._applyRule()
		self.applyingRule = prevApplyingRule
		return res

