def x():
	try:
		yield 1
	except:
		print('pox')
	yield 2


c = x()
next(c)
c.close()
