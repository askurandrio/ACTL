
class MetaOpCode(type):
    def __eq__(self, item):
        return isinstance(item, self) or (isinstance(item, type) and issubclass(self, item))
    
    def __ne__(self, item):
        return not (self == item)


class AnyOpCode(metaclass=MetaOpCode):

    def __eq__(self, item):
        return isinstance(item, AnyOpCode)
    
    def __ne__(self, item):
        return not (self == item)
