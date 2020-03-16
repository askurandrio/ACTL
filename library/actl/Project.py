
import os
import copy
import logging

import yaml


LOGGER = logging.getLogger('actl')
DIR_LIBRARY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Project:
	_DEFAULT_HANDLERS = {}

	def __init__(self, projectf=None, source=(), this=None):
		self.data = {'handlers': copy.copy(self._DEFAULT_HANDLERS)}

		if this is not None:
			self.data = {**self.data, 'this': this}

		if projectf is not None:
			self.data = {**self.data, 'projectf': projectf}
			source = ({'include': projectf},) + tuple(source)

		self.processSource(source)

	@property
	def this(self):
		return self.data.get('this', self)

	def processSource(self, source):
		if isinstance(source, dict):
			source = source.items()

		source = list(source)
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

	def __repr__(self):
		if 'projectf' in self.data:
			head = 'projectf={!r}'.format(self.data['projectf'])
		else:
			head = f'source={self.data}'
		return f'{type(self).__name__}({head})'


@Project.add_default_handler('include')
def _(project, projectf):
	filename = os.path.join(DIR_LIBRARY, 'projects', f'{projectf}.yaml')
	source = yaml.load(open(filename), Loader=yaml.SafeLoader)
	subProject = type(project)(source=source, this=project.this)
	project[projectf] = subProject
	_recursiveUpdate(project.data, subProject.data)


@Project.add_default_handler('py-code')
def _(project, arg):
	exec(arg, {'this': project.this, 'project': project}, None)  # pylint: disable=exec-used


def _recursiveUpdate(base, new):
	for key, value in new.items():
		if isinstance(value, dict):
			base[key] = base.get(key, {})
			_recursiveUpdate(base[key], value)
		elif key not in base:
			base[key] = value
