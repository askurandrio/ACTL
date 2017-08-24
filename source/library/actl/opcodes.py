
class MetaOpCode(type):
    def __eq__(self, item):
        return isinstance(item, self) or (isinstance(item, type) and issubclass(self, item))
    
    def __ne__(self, item):
        return not (self == item)


class AnyOpCode(metaclass=MetaOpCode):
    def __init__(self):
        pass

    def __eq__(self, item):
        return isinstance(item, self.__class__)
    
    def __ne__(self, item):
        return not (self == item)


class SET(AnyOpCode):
    def __init__(self, name, value):
        self.name = name
        self.value = value       

    def __repr__(self):
        return f'{self.name} = {self.value}'


CODE_OPEN = type('CodeOpen', (AnyOpCode,), {})()
CODE_CLOSE = type('CodeClose', (AnyOpCode,), {})()
