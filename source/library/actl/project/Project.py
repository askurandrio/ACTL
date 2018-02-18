
import os

import yaml

from ..code.Code import Code
from ..parser import Parser


DIR_LIBRARY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Project:
	add_syntax = property(lambda self: self.data['rules'].add)

	def __init__(self, projectf=None, data=None):
		if data is None:
			self.data = yaml.load(open(projectf))
		else:
			self.data = data
		self.__class__.this = self
		self.__init()

	def parse(self, filename=None, string=None):
		if not string:
			if not filename:
				filename = self.get('mainf')
			string = open(filename, encoding='utf8').read()
		return Parser(string).parse()		

	def build(self, filename=None, string=None, code=None):
		parser = self.parse(filename, string)
		if code is None:
			buff = list(parser)
			code = Code(buff, self.data['rules'], self.data['scope'])
		LinkLayer(code, *self.data['layers']).link()
		return code

	def translate(self, code):
		from actl.TranslateToString import TranslateToString
		tr = TranslateToString()
		tr.translate(code)

	def get(self, *keys, ivalue=None):
		if ivalue is None:
			ivalue = self.data
		for key in keys[:-1]:
			ivalue = self.get(key, ivalue=ivalue)
		value = ivalue[keys[-1]]
		if isinstance(value, dict) and 'pget' in value:
			value = eval(value['pget'])()
		if isinstance(value, dict) and 'plget' in value:
			if '__value_plget' not in value:
				value['__value_plget'] = eval(value['plget'])()
			return value['__value_plget']
		return value

	def set(self, *keys, value):
		if len(keys) > 1:
			data = self.get(*keys[:-1])
		else:
			data = self.data
		if (keys[-1] in data) and isinstance(data[keys[-1]], dict) and ('pset' in data[keys[-1]]):
			eval(value['pset'])(value)
		else:
			data[keys[-1]] = value

	@property
	def translator(self):
		return self.get('translator', 'value')

	def __init(self):
		this = self.this
		for pcommand in list(self.data):
			if pcommand == 'from':
				projectf = os.path.join(DIR_LIBRARY, 'std', f"{self.data['from']}.yaml")
				project = type(self)(projectf=projectf)
				self.data.update(project.data)
				self.__class__.this = this
			elif pcommand == 'on_init':
				for idx, ocommand in enumerate(self.data['on_init']):
					if ocommand[0] == 'set':
						self.data[self.get('on_init', idx, 1)] = self.get('on_init', idx, 2)


class LinkLayer:
	def __init__(self, code, *layers):
		self.code = code
		self.layers = [layer(self.code) for layer in layers]

	def link(self):
		while self.__link():
			pass

	def __link(self):
		old_hash = hash(self.code)
		self.code.transform()
		for layer in self.layers:
			layer.transform()
		return old_hash != hash(self.code)
