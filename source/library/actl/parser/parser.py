import pyparsing

from .opcodes import Word, Operator


pyparsing.ParserElement.setDefaultWhitespaceChars(' ')


def remove_start(string, template):
	if string.startswitch(template):
		return string[len(template):]
	raise RuntimeError('Template not found')


class Parser:
	def __init__(self, buff):
		self.buff = buff
		self.rules = self.__get_rules()
		self.shifts = []
		self.prev_code = Operator(None)

	def __delete_shifts(self):
		if self.prev_code == Operator('line_end'):
			for idx, shift in enumerate(self.shifts):
				try:
					self.buff = remove_start(self.buff, shift)
				except RuntimeError:
					for _ in self.shifts[idx:]:
						yield Operator('code_close')
					del self.shifts[idx:]
			if self.buff[0] == ' ':
				yield Operator('code_open')
				self.shifts.append('')
				while self.buff[0] == ' ':
					self.shifts[-1] += ' '
					self.buff = self.buff[1:]

	def __find_opcode(self):
		for rule in self.rules:
			for result, start, end in rule.scanString(self.buff):
				if self.buff[:start].lstrip(' '):
					break
				self.buff = self.buff[end:]
				yield result[0]
				return None
		if self.buff[:start]:
			raise RuntimeError(f'This token not found: "{self.buff[:start]}"')

	def __iter__(self):
		yield Operator('code_open')
		while self.buff:
			yield from self.__delete_shifts()
			yield from self.__find_opcode()
		for _ in self.shifts:
			yield Operator('code_close')
		yield Operator('code_close')

	def __get_rules(self):
		rules = []
		rules.extend(Operator.get_parsers())
		rules.extend(Word.get_parsers())
		return rules
