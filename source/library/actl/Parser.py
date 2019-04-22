
from .Buffer import Buffer


@Buffer.of
def parser(buff, rules):
	while buff:
		for rule in rules:
			res = rule(buff)
			if res:
				res(buff)
				break
		else:
			yield buff.pop(0)
