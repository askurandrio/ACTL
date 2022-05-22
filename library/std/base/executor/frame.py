class Frame:
	_default = object()

	def __init__(self, head):
		self._head = iter(head)

	def __await__(self):
		yield from self._head
