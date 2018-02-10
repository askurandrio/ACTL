
import os
import copy

import yaml

from std.py import RULES

from ..code.Code import Code
from ..parser import Parser


DIR_LIBRARY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Project:
	def __init__(self, mainf, projectf):
		self.__data = {}
		self.__load(projectf)
		self.__class__.this = self
		self.compile(mainf)

	def parse(self, filename=None, string=None):
		if filename is not None:
			string = open(filename, encoding='utf8').read()
		return Parser(string).parse()

	def compile(self, filename=None, string=None, code=None):
		from pyport import EExecutor, Scope

		parser = self.parse(filename, string)
		if code is None:
			buff = list(parser)
			code = Code(buff, RULES, Scope())
		LinkLayer(code, EExecutor).link()

		from actl.TranslateToString import TranslateToString
		tr = TranslateToString()
		tr.translate(code)

	def get(self, *keys, ivalue=None):
		if ivalue is None:
			ivalue = self.__data
		for key in keys[:-1]:
			ivalue = self.get(key, ivalue=ivalue)
		value = ivalue[keys[-1]]
		if isinstance(value, dict) and 'evalv' in value:
			value = eval(value['evalv'])
		return value

	def __load(self, projectf):
		self.__data.update(yaml.load(open(projectf)))


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
