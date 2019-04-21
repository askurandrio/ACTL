
from .Buffer import Buffer


@Buffer.of
def parser(buff, rules):
	while buff:
		for rule in rules:
			if rule(buff):
				rule.apply(buff)
				break
		else:
			yield from buff.pop(0)
