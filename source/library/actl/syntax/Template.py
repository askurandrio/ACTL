from .Result import Result


class Template:
	def __init__(self, *template):
		self._template = template

	def __call__(self, buff):
		res = None
		for tmpl in self._template:
			if res is None:
				res = tmpl(buff)
			else:
				res += tmpl(buff)
			if not res:
				break
			buff = res.shift(buff)
		return res

	def __repr__(self):
		return f'{type(self).__name__}({self._template})'


def CustomRule(func):
	def rule(buff):
		try:
			token = buff[0]
		except IndexError:
			return Result(None)
		if func(token):
			return Result(1)
		return Result(None)
	return rule


def Many(*template, min_matches=1):
	template = Template(*template)
	
	def rule(buff):
		base_res = template(buff)
		if not base_res:
			if min_matches < 1:
				return Result(0)
			return base_res
		matches = 1
		while True:
			buff = base_res.shift(buff)
			res = template(buff)
			if res:
				matches += 1
				base_res += res
			else:
				if matches < min_matches:
					return Result(None)
				return base_res
	return rule


def Or(*templates):
	def rule(buff):
		for template in templates:
			res = template(buff)
			if res:
				return res
		return Result(None)
	return rule
