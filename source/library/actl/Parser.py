
from actl.code.opcodes import END_LINE
from .Buffer import Buffer


@Buffer.make
def parser(buff, rules):
	src = Buffer()
	while buff:
		for rule in rules:
			res = rule(buff)
			if res:
				res()
				buff[:0] = src
				src = Buffer()
				break
		else:
			src.append(buff.pop(0))
			if END_LINE in src:
				idx_end_line = src.index(END_LINE)
				res = src[:idx_end_line]
				del src[:idx_end_line]
				yield from res
	yield from src
