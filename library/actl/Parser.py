from actl.Buffer import Buffer


class Parser:
	def __init__(self, scope, rules, buff):
		self.scope = scope
		self.rules = rules
		self.buff = buff
		self._definition = Buffer()

	def define(self, *opcodes):
		self._definition.append(*opcodes)

	def subParser(self, buff=None):
		return type(self)(self.scope, self.rules, buff)

	def _apply_rule(self, buff):
		for rule in self.rules:
			res = rule(self, buff)
			if res:
				return True
		return False

	def parseUntil(self, buff, until):
		flush = Buffer()
		while (until not in flush) and buff:
			if self._apply_rule(buff):
				buff = flush + buff
				flush = Buffer()
				continue

			flush.append(buff.pop())

		if until in flush:
			idx_end_line = flush.index(until)
			res = flush[:idx_end_line]
			del flush[:idx_end_line]
		else:
			res = flush
			flush = Buffer()

		res = self._definition + res
		self._definition = Buffer()
		newBuff = flush + buff
		return res, newBuff

	def __iter__(self):
		while self.buff:
			res, self.buff = self.parseUntil(self.buff, '\n')
			if self.buff and (self.buff[0] == '\n'):
				self.buff.pop()
			yield from res
