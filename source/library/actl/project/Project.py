
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
	__data = collections.OrderedDict()
	__data['handlers'] = {}
	add_syntax = property(lambda self: self[('rules',)].add)

	def __init__(self, projectf=None, source=None, data=None):
		self.__data = copy.deepcopy(self.__data)
		self.source = []
		if data is not None:
			self.update(data)
		if projectf is not None:
			self.source.extend(yaml.load(open(projectf)))
		if source is not None:
			self.source.extend(source)
		self.__init()

	def update(self, data):
		self.__data.update(data)

	def __init(self):
		while self.source:
			elem = list(self.source.pop(0).items())
			assert len(elem) == 1, elem
			key, value = elem[0]
			handlers = self[('handlers',)]
			if ' ' in key:
				key = key.split(' ')
				classes, key = key[:-1], key[-1]
				for cls in classes:
					handlers[cls](self, key, value)
			else:
				if key in handlers:
					handlers[key](self, key, value)
				else:
					self[(key,)] = value

	def __iter__(self):
		return iter(self.__data.items())

	def __contains__(self, key):
		return key in self.__data

	def __getitem__(self, keys):
		value = self.__data
		for key in keys:
			value = value[key]
		if isinstance(value, VirtualProjectItem):
			value = value.get()
		return value

	def __setitem__(self, keys, value):
		base = self[keys[:-1]]
		key = keys[-1]
		if (key in base) and isinstance(base[key], VirtualProjectItem):
			base[key].set(value)
		else:
			base[key] = value

	def __delitem__(self, keys):
		base = self[keys[:-1]]
		key = keys[-1]
		if isinstance(base[key], VirtualProjectItem):
			base[key].delete()
		else:
			del base[key]

	@classmethod
	def add_handler(cls, key):
		def decorator(value):
			cls.__data['handlers'][key] = value
			return value
		return decorator


class VirtualProjectItem:
	def get(self):
		raise NotImplementedError

	def set(self, value):
		raise NotImplementedError

	def delete(self, value):
		raise NotImplementedError


@Project.add_handler('import')
def _(project, _, project_name):
	child_project = type(project)(
		projectf=os.path.join(DIR_LIBRARY, 'std', f'{project_name}.yaml')
	)
	project.update(child_project)
	project[(project_name,)] = child_project


@Project.add_handler('pydef')
def _(project, key, body):
	body = body.replace('\n', '\n  ')
	body = f'def {key}:\n  {body}'
	lc_scope = {}
	try:
		exec(body, {'this': project}, lc_scope)
	except:
		print(f"{project}['{key}']")
		print(body)
		raise
	key = key[:key.find('(')]
	project[(key,)] = lc_scope[key]


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
