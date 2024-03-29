from actl.objects import Object, While


def test_ObjectAsPyStr():
	assert str(Object) == "class 'Object'"


async def test_objectAsPyStr():
	obj = await Object.call()
	assert str(obj) == "Object<>"


async def test_recursiveObjectAsStr():
	obj = await Object.call()
	await obj.setAttribute('obj', obj)
	assert str(obj) == 'Object<obj=↑...>'


async def test_strWhile():
	assert str(While) == "class 'While'"
	assert str(await While.call(())) == 'While<conditionFrame=()>'
