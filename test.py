# counter = 0
# incr = lambda num: num + 1
# cond = lambda num: num < 15000
#
# while cond(counter):
#    counter = incr(counter)


for _ in range(100000):
    __import__('pytest')

#
# def check():
#     breakpoint()
#
# from multiprocessing import Process
# process = Process(target=check)
# process.start()
# process.join()
