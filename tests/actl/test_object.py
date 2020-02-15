from actl.objects import Object, String


def test_object():
	obj = Object.call()
	s = String.call('')
	str(obj)
	str(s)
