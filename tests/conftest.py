import traceback
import signal
import inspect
import importlib
import os
from functools import singledispatch
from itertools import zip_longest

import pytest

from actl.Buffer import Buffer
from actl.objects import AObject
from actl.utils import executeSyncCoroutine
from actl.opcodes import DynamicOpCode


@pytest.fixture
def debugStuck():
	def debug(_, frame):
		print(traceback.format_stack(frame))
		breakpoint()  # pylint: disable=forgotten-debug-statement

	signal.signal(signal.SIGALRM, debug)
	signal.alarm(20)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):  # pylint: disable=unused-argument
	outcome = yield
	rep = outcome.get_result()
	setattr(item, "rep_" + rep.when, rep)
	return rep


def pytest_collection_modifyitems(
	session, config, items
):  # pylint: disable=unused-argument
	def getKey(item):
		filePath, _, _1 = item.location
		filePath = filePath.replace('.py', '')
		order_keys = []

		while filePath != '':
			moduleName = filePath.replace('/', '.')
			module = importlib.import_module(moduleName)
			order_key = getattr(module, 'ORDER_KEY', float('inf'))
			order_keys.insert(0, order_key)
			filePath = os.path.dirname(filePath)

		return order_keys

	items.sort(key=getKey)


def pytest_assertrepr_compare(op, left, right):  # pylint: disable=unused-argument
	if isinstance(left, (Buffer, list, tuple, AObject, DynamicOpCode, dict)):
		res = [''] + _getDiff(left, right, '')
		return res
	return None


_default = object()


def _getDiff(leftObject, rightObject, indent):
	left = _toTuple(leftObject)
	if isinstance(rightObject, (Buffer, list, tuple, AObject, DynamicOpCode, dict)):
		right = _toTuple(rightObject)
	else:
		return [
			f'{indent}	left is {leftObject}',
			f'{indent}	right is {rightObject}',
			f'{indent}	right type<{type(rightObject).__name__}> is unexpected',
		]

	res = [f'{indent}{leftObject} != ', f'{indent}{rightObject}']

	for idx, (first, second) in enumerate(zip_longest(left, right, fillvalue=_default)):
		if first == second:
			continue

		res += [f'{indent}at {idx}']

		if first is _default:
			return [*res, f'{indent}	first is empty, second is {second}']

		if second is _default:
			return [*res, f'{indent}	second is empty, first is {first}']

		if isinstance(first, (Buffer, list, tuple, AObject, DynamicOpCode, dict)):
			return [*res, *_getDiff(first, second, indent + '	')]

		return [*res, f'{indent}	{repr(first)} != {repr(second)}']

	return [
		f'{indent}{type(leftObject)}{leftObject} != ',
		f'{indent}{type(rightObject)}{rightObject}',
	]


@singledispatch
def _toTuple(arg):
	if isinstance(arg, DynamicOpCode):
		return _toTuple.dispatch(DynamicOpCode)(arg)

	raise RuntimeError(f'{type(arg)}{(arg)} is unexpected')


@_toTuple.register(Buffer)
@_toTuple.register(list)
@_toTuple.register(tuple)
def _toTuple__iter(arg):
	return tuple(arg)


@_toTuple.register(dict)
def _toTuple__dict(arg):
	return tuple(sorted(arg.items(), key=lambda pair: pair[0]))


@_toTuple.register
def _toTuple__Object(arg: AObject):
	return _toTuple(arg.head)


@_toTuple.register
def _toTuple__DynamicOpCode(arg: DynamicOpCode):
	res = [('type', type(arg))]
	res.extend((attr, getattr(arg, attr)) for attr in type(arg).__slots__)
	return tuple(res)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_pyfunc_call(pyfuncitem):
	pyfuncitem.obj = _wrapAsyncFunction(pyfuncitem.obj)

	yield


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):  # pylint: disable=unused-argument
	if inspect.iscoroutinefunction(fixturedef.func):
		fixturedef.func = _wrapAsyncFunction(fixturedef.func)

	yield


def _wrapAsyncFunction(function):
	def wrapper(*args, **kwargs):
		result = function(*args, **kwargs)

		if inspect.iscoroutine(result):
			result = executeSyncCoroutine(result)

		return result

	return wrapper
