
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
	this = None
	__data = collections.OrderedDict()
	__data['handlers'] = {}
	add_syntax = property(lambda self: self[('rules',)].add)

	def __init__(self, projectf=None, source=None, data=None):
		if type(self).this is None:
			type(self).this = self
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

	def __getitem__(self, keys, data=None):
		value = data or self.__data
		for key in keys:
			value = value[key]
		if isinstance(value, VirtualProjectItem) and hasattr(value, 'get'):
			value = value.get()
		return value

	def __setitem__(self, keys, value, base=None):
		base = base or self[keys[:-1]]
		key = keys[-1]
		if (key in base) and isinstance(base[key], VirtualProjectItem) and hasattr(value, 'set'):
			base[key].set(value)
		else:
			base[key] = value

	def __delitem__(self, keys):
		base = self[keys[:-1]]
		key = keys[-1]
		if isinstance(base[key], VirtualProjectItem) and hasattr(base[key], 'delete'):
			base[key].delete()
		else:
			del base[key]

	@classmethod
	def add_handler(cls, key):
		def decorator(value):
			cls.__data['handlers'][key] = value
			return value
		return decorator

	def __repr__(self):
		return f'{type(self).__name__}({self.__data})'


class SubProject(Project):
	def __init__(self, project, source):
		self.__data = {}
		super().__init__(data=project, source=source)

	def update(self, data):
		self.__data.update(data)

	def __iter__(self):
		return iter(self.__data.items())

	def __getitem__(self, keys):
		try:
			return super().__getitem__(keys)
		except KeyError:
			return super().__getitem__(keys, data=self.__data)

	def __setitem__(self, keys, value):
		super().__setitem__(keys, value, base=self[keys[:-1]])

	def __repr__(self):
		return f'{type(self).__name__}(project={super().__repr__()}, data={self.__data})'

class VirtualProjectItem:
	def __init__(self, project, key, value):
		self._project = project
		self._key = key
		self._value = value
		self._project[(self._key,)] = self

	def __repr__(self):
		return f'{type(self).__name__}(key={self._key}, value={self._value})'


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
		exec(body, {'this': type(project).this}, lc_scope)
	except:
		print(f"{project}['{key}']")
		print(body)
		raise
	key = key[:key.find('(')]
	project[(key,)] = lc_scope[key]


@Project.add_handler('pypropl')
class ProjectItemPyPropLazy(VirtualProjectItem):
	def __init__(self, project, key, value):
		super().__init__(project, key, value)

	def get(self):
		try:
			return self.__self
		except AttributeError:
			subproject = SubProject(
				self._project, [{key: value} for key, value in self._value.items()]
			)
			self.__self = subproject[('get',)]()
			return self.get()


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
