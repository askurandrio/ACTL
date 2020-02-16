# pylint: disable=redefined-outer-name, no-member, not-callable
from unittest.mock import Mock

import pytest

from actl import Project, Buffer
from actl.objects import PyToA, AToPy, AFalse


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
	print_ = Mock()

	scope = execute({'print': PyToA.call(print_)}, 'print(1)')

	print_.assert_called_once_with(1)
	assert AToPy(scope['_']) is print_.return_value


def test_while(execute):
	def cond_():
		called, cond_.called = cond_.called, True
		return not called

	cond_.called = False
	cond = Mock(side_effect=cond_)
	print_ = Mock()

	scope = execute({'cond': PyToA.call(cond), 'print': PyToA.call(print_)}, 'while cond(): print(1)')

	assert cond.call_count == 2
	print_.assert_called_once_with(1)
	assert scope['_'].equal(AFalse)
