from unittest.mock import Mock

from actl import Buffer


def test_watch():
	mock = Mock()
	buff = Buffer([1])

	tuple(buff.watch(mock))

	mock.assert_called_once_with(1)


def test_delSlice():
	buff = Buffer(range(5))

	del buff[:2]

	assert buff == [2, 3, 4]


def test_repr():
	buff = Buffer(range(1, 12))

	assert repr(buff) == 'Buffer([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ...])'
