from actl.objects import Object, While


def test_ObjectAsPyStr():
	assert str(Object) == "class 'Object'"


async def test_objectAsPyStr():
	assert str(await Object.call()) == "Object<>"


async def test_recursiveObjectAsStr():
	obj = await Object.call()
	obj.setAttribute('obj', obj)
	assert str(obj) == 'Object<obj=↑...>'


async def test_strWhile():
	assert str(While) == "class 'While'"
	assert str(await While.call([])) == 'While<conditionFrame=[]>'
