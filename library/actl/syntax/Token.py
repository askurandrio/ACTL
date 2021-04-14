from actl.syntax.AbstractTemplate import AbstractTemplate


class Token(AbstractTemplate):
	__slots__ = ('token',)

	def __call__(self, _, inp):
		for idx, element in enumerate(self.token):
			try:
				inpElement = inp[idx]
			except IndexError:
				return None
			if element != inpElement:
				return None

		return inp.shift(len(self.token))
