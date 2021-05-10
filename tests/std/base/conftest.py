import pytest

from tests.std.utils import AbstractExecute


@pytest.fixture
def execute():
	return _Execute()


class _Execute(AbstractExecute):
	_PROJECT_NAME = 'std/base'
