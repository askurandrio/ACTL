from actl.objects import Object, While


def test_str_object():
	assert str(Object) == "class 'Object'"
	assert str(Object.call()) == "Object<{'__class__': class 'Object'}>"


def test_str_while():
	assert str(While) == "class 'While'"
	assert str(While.call([])) == "While<{'__class__': class 'While', 'conditionFrame': []}>"
