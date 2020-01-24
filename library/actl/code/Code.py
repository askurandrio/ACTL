from actl.opcodes import AnyOpCode


class Code(AnyOpCode, list):
	def __init__(self, elems=None):
		if elems is not None:
			self.extend(elems)

	def __repr__(self):
		return f'{type(self).__name__}({", ".join(map(str, self))})'


class Definition(Code):
	def __init__(self, *elems):
		super().__init__(elems)
