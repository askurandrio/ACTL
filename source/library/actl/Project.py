
import os
import copy
import logging
import collections

import yaml


LOGGER = logging.getLogger('actl')
DIR_LIBRARY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
yaml.add_representer(
	collections.OrderedDict, lambda dumper, data: dumper.represent_dict(data.iteritems())
)
yaml.add_constructor(
	yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
	lambda loader, node: collections.OrderedDict(loader.construct_pairs(node))
)
	

class Project:
	_DEFAULT_HANDLERS = {}

	def __init__(self, projectf=None, source=None):
		cls = type(self)
		if not hasattr(cls, 'this'):
			cls.this = self
		if projectf:
			projectf = os.path.join(DIR_LIBRARY, 'projects', f'{projectf}.yaml')
			assert source is None
			source = yaml.load(open(projectf), Loader=yaml.SafeLoader)
		self.data = {'handlers': copy.copy(self._DEFAULT_HANDLERS)}
		self._init(source)

	def _init(self, source):
		if isinstance(source, dict):
			source = list(source.items())
		while source:
			cmd = source.pop(0)
			if isinstance(cmd, dict):
				lcmd = list(cmd.items())
				key, arg = lcmd.pop(0)
				assert not lcmd
			else:
				key, arg = cmd
			handlers = self['handlers']
			if key in handlers:
				handlers[key](self, arg)
			else:
				self[key] = arg

	def __getitem__(self, keys):
		if not isinstance(keys, tuple):
			keys = (keys,)
		value = self.data
		for key in keys:
			value = value[key]
		return value

	def __setitem__(self, keys, value):
		if isinstance(keys, str):
			keys = (keys,)
		base = self.data
		for key in keys[:-1]:
			base = base[key]
		base[keys[-1]] = value
		
	@classmethod
	def add_default_handler(cls, name):
		def decorator(func):
			cls._DEFAULT_HANDLERS[name] = func
			return func
		return decorator

	def __repr__(self):
		return f'{type(self).__name__}(source={self.data})'


@Project.add_default_handler('include')
def _(project, arg):
	sub_project = type(project)(projectf=arg)
	project[arg] = sub_project
	_recursive_update(project.data, sub_project.data)


@Project.add_default_handler('py-code')
def _(project, arg):
	exec(arg, {'this': Project.view, 'project': project}, None)


class ProjectView:
	def __getitem__(self, key):
		return Project.this[key]

	def __setitem__(self, key, value):
		Project.this[key] = value


Project.view = ProjectView()

def _recursive_update(base, new):
	for key, value in new.items():
		if isinstance(value, dict):
			base[key] = base.get(key, {})
			_recursive_update(base[key], value)
		else:
			base[key] = value


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
