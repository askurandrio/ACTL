
class Function:
	def __init__(self, function):
		self.__function = function

	def call(self):
		self.__function()

	@classmethod
	def fromPy(cls, function):
		return cls(function)
