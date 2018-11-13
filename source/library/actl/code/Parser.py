
from ..Buffer import Buffer
from ..tokenizer import tokens
from ..syntax import Command
from .Code import Code, Definition


class Parser:
	def __init__(self, buff, scope, rules):
		self.buff = buff
		self.scope = scope
		self.rules = rules

	def is_matching(self):
		for idx_start, _ in enumerate(self.buff):
			for rule in self.rules:
				result_match = rule.match(self.scope, self.buff[idx_start:])
				if result_match or result_match.is_matching():
					return idx_start - 1
		return None

	def parse(self):
		while self.is_matching() is not None:
			self.__apply_rule()
		while self.__after_compile():
			pass
		return self.buff

	def get_definition(self, idx):
		while (idx > 0) and \
				(tokens.OPERATOR('line_end') != self.buff[idx]):
			idx -= 1
		if idx > 0:
			idx += 1
		if Definition != self.buff.get(idx):
			self.buff.insert(idx, Definition())
		return self.buff[idx]

	def __apply_rule(self):
		for idx_start, _ in enumerate(self.buff):
			for rule in self.rules:
				result_match = rule.match(self.scope, self.buff[idx_start:])
				if result_match:
					result = rule(self.scope, self.buff.child(idx_start))
					if rule.in_context:
						return True
					self.__insert_result(idx_start, result)
					return True

	def __insert_result(self, idx_start, result):
		src_idx_start = idx_start
		definition = None
		for opcode in result:
			if Definition == opcode:
				if definition is None:
					definition = Definition()
				definition.extend(opcode)
			elif isinstance(opcode, Command):
				self.__execute_command(opcode)
			else:
				self.buff.insert(idx_start, opcode)
				idx_start += 1
		if definition is not None:
			self.get_definition(src_idx_start).extend(definition)

	def __after_compile(self):
		for idx, opcode in enumerate(self.buff):
			if Code == opcode:
				self.buff[idx] = self.__execute_command(Command('compile', opcode))

	def __execute_command(self, command):
		if command.command == 'compile':
			parser = type(self)(Buffer(*command.args), self.scope, self.rules)
			parser = type(self)(Buffer(*command.args), self.scope, self.rules)
			code = type(*command.args)()
			code.extend(parser.parse())
			return code
		else:
			raise RuntimeError(f'This command not found: {command}')
