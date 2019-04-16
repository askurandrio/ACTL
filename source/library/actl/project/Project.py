
import os
import copy
import logging
import collections

import yaml


LOGGER = logging.getLogger('actl')
DIR_LIBRARY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
		if projectf:
			projectf = os.path.join(DIR_LIBRARY, 'projects', f'{projectf}.yaml')
			assert source is None
			source = yaml.load(open(projectf))
		self.data = {'handlers': copy.copy(self._DEFAULT_HANDLERS)}
		self._init(source)

	def _init(self, source):
		while source:
			cmd = list(source.pop(0).items())
			key, arg = cmd.pop(0)
			assert not cmd
			self['handlers'][key](self, key, arg)

	def __getitem__(self, *keys):
		value = self.data
		for key in keys:
			value = value[key]
		return value

	def __setitem__(self, *keys, value):
		base = self.data
		for key in keys[:-1]:
			base = base[key]
		base[keys[-1]] = value

	def __delitem__(self, keys):
		base = self.data
		for key in keys[:-1]:
			base = base[key]
		del base[keys[-1]]

	@classmethod
	def add_default_handler(cls, name):
		def decorator(func):
			cls._DEFAULT_HANDLERS[name] = func
			return func
		return decorator

	def __repr__(self):
		return f'{type(self).__name__}(source={self.data})'


@Project.add_default_handler('include')
def _(project, _, arg):
	sub_project = type(project)(projectf=arg)
	_recursive_update(sub_project.data, sub_project.data)


class VirtualProjectItem:
	def __init__(self, project, key, value):
		self._project = project
		self._key = key
		self._value = value
		self._project[(self._key,)] = self

	def __repr__(self):
		return f'{type(self).__name__}(key={self._key}, value={self._value})'


#@Project.add_handler('import')
def _(project, _, project_name):
	child_project = type(project)(
		projectf=os.path.join(DIR_LIBRARY, 'std', f'{project_name}.yaml')
	)
	project.update(child_project)
	project[(project_name,)] = child_project


#@Project.add_handler('pydef')
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


#@Project.add_handler('pypropl')
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
