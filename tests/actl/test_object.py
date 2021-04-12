from actl.objects import Object, While


def test_ObjectAsPyStr():
	assert str(Object) == "class 'Object'"


def test_objectAsPyStr():
	assert str(Object.call.obj().obj) == "Object<{}>"


def test_recursiveObjectAsStr():
	obj = Object.call.obj().obj
	obj.setAttribute('obj', obj)
	assert str(obj) == "Object<{'obj': {...}}>"


def test_strWhile():
	assert str(While) == "class 'While'"
	assert str(While.call.obj([]).obj) == "While<{'conditionFrame': []}>"
