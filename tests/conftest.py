import traceback
import signal
from functools import singledispatch
from itertools import zip_longest

import pytest
import os
from actl import objects

from actl.Buffer import Buffer
from actl.objects import Object
from actl.opcodes import DynamicOpCode


@pytest.fixture
def debugStuck():
	def debug(_, frame):
		print(traceback.format_stack(frame))
		breakpoint()

	signal.signal(signal.SIGALRM, debug)
	signal.alarm(20)


def pytest_assertrepr_compare(op, left, right):
	if isinstance(left, (Buffer, list, tuple, type(Object), DynamicOpCode)):
		res = [''] + _getDiff(left, right, '')
		return res
	return None


_default = object()


def _getDiff(leftObject, rightObject, indent):
	left = _toTuple(leftObject)
	if isinstance(rightObject, (Buffer, list, tuple, type(Object), DynamicOpCode)):
		right = _toTuple(rightObject)
	else:
		return [
			f'{indent}	left is {left}',
			f'{indent}	right is {rightObject}',
			f'{indent}	right type<{type(rightObject).__name__}> is unexpected'
		]

	res = [
		f'{indent}{left} != ',
		f'{indent}{right}'
	]

	for idx, (first, second) in enumerate(zip_longest(left, right, fillvalue=_default)):
		if first == second:
			continue

		res += [f'{indent}at {idx}']

		if first is _default:
			return [
				*res,
				f'{indent}	first is empty, second is {second}'
			]

		if second is _default:
			return [
				*res,
				f'{indent}	second is empty, first is {first}'
			]

		if isinstance(first, (Buffer, list, tuple, type(Object), DynamicOpCode)):
			return [
				*res,
				*_getDiff(first, second, indent + '	')
			]

		return [
			*res,
			f'{indent}	{repr(first)} != {repr(second)}'
		]

	return [
		f'{indent}{type(leftObject)}{leftObject} != ',
		f'{indent}{type(rightObject)}{rightObject}'
	]


@singledispatch
def _toTuple(arg):
	if isinstance(arg, DynamicOpCode):
		return _toTuple.dispatch(DynamicOpCode)(arg)

	raise RuntimeError(f'{type(arg)}{(arg)} is unexpected')


@_toTuple.register(Buffer)
@_toTuple.register(list)
@_toTuple.register(tuple)
def _(arg):
	return tuple(arg)


@_toTuple.register
def _(arg: type(Object)):
	return tuple(sorted(arg._head.items(), key=lambda pair: pair[0]))


@_toTuple.register
def _(arg: DynamicOpCode):
	res = [('type', type(arg))]
	res.extend((attr, getattr(arg, attr)) for attr in type(arg).__slots__)
	return tuple(res)
