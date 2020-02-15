from unittest.mock import Mock

import pytest

from actl import Project, Buffer
from actl.objects import PyToA, AToPy


@pytest.fixture
def execute():
	def _execute(scope, inp):
		project = Project('std')
		project['scope'].update(scope)
		project['uinput'] = Buffer(inp)
		project['code'] = project['parse']()
		project['execute']()
		return project['scope']

	return _execute


def test_print(execute):
	mock = Mock()

	scope = execute({'print': PyToA.fromPy(mock)}, 'print(1)')

	mock.assert_called_with(1)
	assert AToPy(scope['_']) == mock.return_value
