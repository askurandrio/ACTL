import traceback
import signal
from functools import singledispatch
from itertools import zip_longest

import pytest

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


def _getDiff(left, right, indent):
	left = _toTuple(left)
	if isinstance(right, (Buffer, list, tuple, type(Object), DynamicOpCode)):
		right = _toTuple(right)
	else:
		return [f'{indent}type<{type(right)}> of {right} is unexpected']

	res = [
		f'{indent}{left} != ',
		f'{indent}{right}'
	]

	for idx, (first, second) in enumerate(zip_longest(left, right)):
		if first != second:
			res += [f'{indent}at {idx}']
			if isinstance(first, (Buffer, list, tuple, type(Object), DynamicOpCode)):
				return res + _getDiff(first, second, indent + '   ')
			return [
				*res,
				f'{indent}   {first} != {second}'
			]

	raise RuntimeError


@singledispatch
def _toTuple(arg):
	if isinstance(arg, DynamicOpCode):
		return _toTuple.dispatch(DynamicOpCode)(arg)
	raise RuntimeError(arg)


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
