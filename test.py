counter = 0
incr = lambda num: num + 1
cond = lambda num: num < 15000

while cond(counter):
   counter = incr(counter)
