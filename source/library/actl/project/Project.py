
import os
import copy
import logging
import collections

import yaml


LOGGER = logging.getLogger('actl')
DIR_LIBRARY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def add_orderd_dict_yaml():

	dict_representer = lambda dumper, data: dumper.represent_dict(data.iteritems())
	dict_constructor = lambda loader, node: collections.OrderedDict(loader.construct_pairs(node))

	yaml.add_representer(collections.OrderedDict, dict_representer)
	yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, dict_constructor)
add_orderd_dict_yaml()


def recursice_update(base, update_dict):
	for key, value in update_dict.items():
		if isinstance(value, collections.Mapping):
			base[key] = base.get(key, {})
			recursice_update(base[key], value)
		else:
			base[key] = value


class Project:
	pfunctions = {}
	add_syntax = property(lambda self: self[('rules',)].add)

	def __init__(self, projectf=None, data=None):
		if data is None:
			self.__data = yaml.load(open(projectf))
		else:
			self.__data = data
		self.__class__.this = self
		self.__init()

	def __init(self):
		idx = 0
		while idx < len(self.__data):
			command = list(self.__data)[idx]
			self.pfunctions[command](command)
			idx += 1

	def update(self, data):
		self.__data.update(data)

	def __run_code(self, function, code, lc_scope=None):
		try:
			return function(code, {'this':self}, lc_scope)
		except:
			LOGGER.exception(code)
			raise

	def __init(self):
		if 'from' in self.__data:
			project_name = self[('from',)]
			del self.__data['from']
			project = type(self)(projectf=os.path.join(DIR_LIBRARY, 'std', f"{project_name}.yaml"))
			self.__class__.this = self
			self_data = self.__data
			self.__data = copy.deepcopy(project.__data)
			recursice_update(self.__data, self_data)

	def __getitem__(self, keys, data=None):
		if data is None:
			data = self.__data
		for key in keys[:-1]:
			data = self.__getitem__((key,), data)
		if keys:
			value = data[keys[-1]]
		else:
			return data

		if isinstance(value, dict):
			if 'pget' in value:
				return self.__run_code(eval, value['pget'])
			if 'def pfunction' in value:
				code = 'def pfunction():\n'
				code += '\n'.join(f'   {line}' for line in value['def pfunction'].split('\n'))
				lc_scope = {}
				self.__run_code(exec, code, lc_scope)
				return lc_scope['pfunction']
			if 'pfunction' in value:
				pfunction = self.__getitem__(('pfunction',), value)
				function = self.__run_code(eval, self.__getitem__(('function',), pfunction))
				args = []
				kwargs = {}
				if 'kwargs' in pfunction:
					for key in self.__getitem__(('kwargs',), pfunction):
						kwargs[key] = self.__getitem__(('kwargs', key), pfunction)
				if 'args' in pfunction:
					for idx, _ in enumerate(self.__getitem__(('args',), pfunction)):
						args.append(self.__getitem__(('args', idx), pfunction))
				return function(*args, **kwargs)
		return value

	def __setitem__(self, keys, value):
		data = self[keys[:-1]]
		if (keys[-1] in data) and isinstance(data[keys[-1]], dict) and ('pfset' in data[keys[-1]]):
			self.__run_code(eval, data[keys[-1]]['pfset'])(value)
		else:
			data[keys[-1]] = value


class LinkerLayer:
	def __init__(self, *layers):
		self.__layers = layers

	def link(self):
		idx_layer = 0
		while idx_layer < len(self.__layers):
			opt = self.__layers[idx_layer].link()
			if opt == 'back':
				idx_layer -= 1
			elif opt == 'next':
				idx_layer += 1
			else:
				raise RuntimeError(f'opt from layer<{self.__layers[idx_layer]}> not found: {opt}')
