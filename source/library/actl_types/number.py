from .actl_object import actl_object

class number(actl_object):
    def __init__(self, number):
        self.number = number

    def __repr__(self):
        return f'{self.__class__.__name__}({self.number})'
