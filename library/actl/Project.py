
import os
import copy
import logging

import yaml


LOGGER = logging.getLogger('actl')
DIR_LIBRARY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Project:
	_DEFAULT_HANDLERS = {}

	def __init__(self, projectf=None, source=None, this=None):
		if this is not None:
			self.this = this

		self.data = {'handlers': copy.copy(self._DEFAULT_HANDLERS)}

		if projectf:
			assert source is None
			self.data['projectf'] = projectf
			projectf = self.__resolve_projectf(projectf)
			source = self.yaml_load(open(projectf))

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

		res = self.data
		for key in keys:
			res = res[key]

		return res

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
		return os.path.join(DIR_LIBRARY, 'projects', f'{projectf}.yaml')

	@staticmethod
	def yaml_load(arg):
		return yaml.load(arg, Loader=yaml.SafeLoader)

	def __repr__(self):
		if 'projectf' in self.data:
			head = 'projectf={!r}'.format(self.data['projectf'])
		else:
			head = f'source={self.data}'
		return f'{type(self).__name__}({head})'


@Project.add_default_handler('include')
def _(project, projectf):
	sub_project = type(project)(this=project, projectf=projectf)
	project[projectf] = sub_project
	_recursive_update(project.data, sub_project.data)


@Project.add_default_handler('py-code')
def _(project, arg):
	this = getattr(project, 'this', project)
	exec(arg, {'this': this, 'project': project}, None)  # pylint: disable=exec-used


def _recursive_update(base, new):
	for key, value in new.items():
		if isinstance(value, dict):
			base[key] = base.get(key, {})
			_recursive_update(base[key], value)
		elif key not in base:
			base[key] = value
