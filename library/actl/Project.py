
import os
import copy
import logging

import yaml


LOGGER = logging.getLogger('actl')
DIR_LIBRARY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Project:
	_DEFAULT_HANDLERS = {}

	def __init__(self, projectf=None, source=None):
		cls = type(self)
		if not hasattr(cls, 'this'):
			cls.this = self
		if projectf:
			assert source is None
			projectf = self.__resolve_projectf(projectf)
			source = self.yaml_load(open(projectf))
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

	def __getitem__(self, key):
		return self.data[key]

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

	@classmethod
	def __resolve_projectf(cls, projectf):
		for suggestion in (
			lambda: os.path.join(DIR_LIBRARY, 'projects', f'{projectf}.yaml'),
			lambda: os.path.abspath(projectf)
		):
			path = suggestion()
			if os.path.exists(path):
				return path
		raise RuntimeError(f'Can not resolve this projectf: {projectf}')

	@staticmethod
	def yaml_load(arg):
		return yaml.load(arg, Loader=yaml.SafeLoader)

	def __repr__(self):
		return f'{type(self).__name__}(source={self.data})'


@Project.add_default_handler('include')
def _(project, arg):
	kwargs = {}
	if isinstance(arg, str):
		kwargs['projectf'] = arg
	elif isinstance(arg, Project):
		kwargs['source'] = arg.data
	else:
		kwargs['source'] = arg
	sub_project = type(project)(**kwargs)
	project[arg] = sub_project
	_recursive_update(project.data, sub_project.data)


@Project.add_default_handler('py-code')
def _(project, arg):
	exec(arg, {'this': Project.view, 'project': project}, None)  # pylint: disable=exec-used


class ProjectView:
	def __getitem__(self, key):
		return Project.this[key]  # pylint: disable=no-member

	def __setitem__(self, key, value):
		Project.this[key] = value  # pylint: disable=no-member


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
