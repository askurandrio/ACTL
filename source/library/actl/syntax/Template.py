
class Template:
	def __init__(self, *template):
		self.__template = [self.create(tmpl) for tmpl in template]

	def match(self, scope, buff):
		result = ResultMatch(0, False)
		template = iter(self.__template)

		for tmpl in template:
			result_rule = tmpl.match(scope, buff[result.idx_end:])
			if result_rule:
				result += result_rule
			else:
				return result_rule
		return result

	def __contains__(self, item):
		for tmpl in self.__template:
			if item not in tmpl:
				return False
		return True

	@classmethod
	def create(cls, template):
		from .modules import OneOpcode

		if not isinstance(template, Template):
			template = OneOpcode(template)
		return template

	def __repr__(self):
		return f'{type(self).__name__}({self.__template})'


class ResultMatch:
	def __init__(self, idx_end=None, is_find=None):
		self.__idx_end = idx_end
		self.__is_find = is_find
		if self.__is_find is None:
			assert self.__idx_end is not None
			self.__is_find = True

	def convert_to_false(self):
		return type(self)(idx_end=self.__idx_end, is_find=False)

	def is_matching(self):
		return bool(self.__idx_end)

	def is_find(self):
		return bool(self.__is_find)

	@property
	def idx_end(self):
		assert self.__idx_end is not None
		return self.__idx_end

	def __add__(self, other):
		idx_end = self.idx_end if self.is_matching() else 0
		idx_end += other.idx_end if other.is_matching() else 0
		return type(self)(idx_end, self.is_find() or other.is_find())

	def __bool__(self):
		return self.is_find()

	def __repr__(self):
		return f'ResultMatch(idx_end={self.__idx_end}, is_find={self.is_find()})'
