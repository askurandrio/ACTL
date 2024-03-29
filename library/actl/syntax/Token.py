from actl.syntax.AbstractTemplate import AbstractTemplate


class Token(AbstractTemplate):
	__slots__ = ('token',)

	async def __call__(self, _, inp):
		for idx, element in enumerate(self.token):
			try:
				inpElement = inp[idx]
			except IndexError:
				return None
			if element != inpElement:
				return None

		res = inp[: len(self.token)]
		del inp[: len(self.token)]
		return res

	@classmethod
	def of(cls, element):
		return cls((element,))
