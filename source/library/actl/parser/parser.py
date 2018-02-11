import pyparsing

from .tokens import INDENT, VARIABLE, STRING, OPERATOR


pyparsing.ParserElement.setDefaultWhitespaceChars(' ')


class Parser:
	def __init__(self, buff):
		self.buff = buff
		self.rules = self.__get_rules()
		self.indents = []
		self.prev_code = OPERATOR(None)

	def __delete_indents(self, force=False):
		if (self.prev_code != OPERATOR('line_end')) and (not force):
			return None

		for idx, indent in enumerate(self.indents):
			if self.buff.startswith(indent.string):
				yield indent
				self.buff = self.buff[len(indent.string):]
			else:
				del self.indents[idx:]
				break

		if self.buff and ((self.buff[0] == ' ') or (self.buff[0] == '	')):
			tmpl = self.buff[0]
			indent = INDENT('')
			while self.buff and (self.buff[0] == tmpl):
				indent.string += self.buff[0]
				self.buff = self.buff[1:]
			if self.buff:
				assert (self.buff[0] != ' ') or (self.buff[0] != '	')
			self.indents.append(indent)
			yield indent

	def __find_opcode(self):
		for rule in self.rules:
			for result, start, end in rule.scanString(self.buff):
				if self.buff[:start].lstrip(' '):
					break
				self.buff = self.buff[end:]
				self.prev_code = result[0]
				yield result[0]
				return None
		if self.buff[:start]:
			raise RuntimeError(f'This token not found: "{self.buff[:start]}"')

	def parse(self):
		yield OPERATOR('code_open')
		yield from self.__delete_indents(force=True)
		while self.buff:
			yield from self.__find_opcode()
			yield from self.__delete_indents()
		yield OPERATOR('code_close')

	def __get_rules(self):
		rules = []
		rules.extend(VARIABLE.get_parsers())
		rules.extend(STRING.get_parsers())
		rules.extend(OPERATOR.get_parsers())
		return rules
