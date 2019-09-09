

from .Buffer import Buffer


class InitAsCreate(type):
	def __call__(self, *args, **kwargs):
		init = super().__call__
		return self._create(init, *args, **kwargs)


class ResultIsBuffer(InitAsCreate):
	@staticmethod
	def _create(init, *args, **kwargs):
		return Buffer(init(*args, **kwargs))
