
class MetaOpCode(type):
    def __eq__(self, item):
        return isinstance(item, self) or (isinstance(item, type) and issubclass(self, item))
    
    def __ne__(self, item):
        return not (self == item)


class AnyVirtualOpCode(metaclass=MetaOpCode):
    def __init__(self):
        pass

    def __eq__(self, item):
        return isinstance(item, AnyVirtualOpCode)
    
    def __ne__(self, item):
        return not (self == item)


class AnyOpCode(AnyVirtualOpCode):
    def __eq__(self, item):
        return isinstance(item, AnyOpCode)


class Name(AnyOpCode):
    COUNT_TEMP_NAME = -1

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_temp_name(cls):
        cls.COUNT_TEMP_NAME += 1
        return cls(f'R{cls.COUNT_TEMP_NAME}')

    def __repr__(self):
        return f'{self.name}'


class SET(AnyOpCode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'{self.name} = {self.value}'


class LOAD_ATTRIBUTE(AnyOpCode):
    def __init__(self, obj, attribute):
        self.obj = obj
        self.attribute = attribute

    def __repr__(self):
        return f'{self.__class__.__name__}({self.obj}, {self.attribute})'


CODE_OPEN = type('CodeOpen', (AnyOpCode,), {})()
CODE_CLOSE = type('CodeClose', (AnyOpCode,), {})()
