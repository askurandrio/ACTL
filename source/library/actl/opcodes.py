
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
        return isinstance(item, self.__class__)


class Variable(AnyOpCode):
    COUNT_TEMP_VARIABLE = -1

    def __init__(self, name=None):
        if isinstance(name, self.__class__):
            self.name = name.name
        else:
            self.name = name

    def __eq__(self):
        return AnyOpCode.__eq__(self, item) and (self.name == item.name)

    @classmethod
    def get_temp_variable(cls):
        cls.COUNT_TEMP_VARIABLE += 1
        return cls(f'R{cls.COUNT_TEMP_VARIABLE}')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'


class DECLARE:
    def __init__(self, type=None, name=None):
        self.type = Variable(type)
        self.name = Variable(name)

    def get_variable(self):
        return self.name

    def __repr__(self):
        return f'{self.__class__.__name__}({self.type}, {self.name})'


class SET(AnyOpCode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'SET({self.name.name}, {self.value})'


class LOAD_ATTRIBUTE(AnyOpCode):
    def __init__(self, obj, attribute):
        self.obj = obj
        self.attribute = attribute

    def __repr__(self):
        return f'{self.__class__.__name__}({self.obj}, {self.attribute})'


CODE_OPEN = type('CodeOpen', (AnyOpCode,), {})()
CODE_CLOSE = type('CodeClose', (AnyOpCode,), {})()
