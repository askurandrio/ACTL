
class Result:
	def __init__(self, idx_end):
		self.idx_end = idx_end

	def shift(self, buff):
		return buff[self.idx_end:]

	def __iadd__(self, other):
		self.idx_end += other.idx_end
		return self

	def __bool__(self):
		return self.idx_end is not None

	def __repr__(self):
		return f'{type(self).__name__}({self.idx_end})'
