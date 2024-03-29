import actl


class Parser(actl.Parser):
	def __init__(self, *args, **kwargs):
		self.applyingRule = False
		super().__init__(*args, **kwargs)

	async def _applyRule(self):
		prevApplyingRule, self.applyingRule = self.applyingRule, True
		res = await super()._applyRule()
		self.applyingRule = prevApplyingRule
		return res

	async def parseLine(self):
		res = await super().parseLine()
		res.loadAll()

		if res:
			res += self._genPrintLastResult(res[-1])

		return res

	@staticmethod
	def _genPrintLastResult(opcode):
		if type(opcode) in (
			actl.opcodes.SET_VARIABLE,
			actl.opcodes.SET_ATTRIBUTE,
			actl.opcodes.RETURN,
		):
			return ()

		if actl.opcodes.VARIABLE == opcode:
			name = opcode.name
		else:
			name = opcode.dst

		return (actl.opcodes.CALL_FUNCTION(dst='_', function='print', args=[name]),)
