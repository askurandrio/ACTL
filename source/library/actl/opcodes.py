
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
        self.name = name

    def __eq__(self):
        return AnyOpCode.__eq__(self, item) and (self.name == item.name)

    @classmethod
    def get_temp_variable(cls, _type=None):
        cls.COUNT_TEMP_VARIABLE += 1
        return cls(f'R{cls.COUNT_TEMP_VARIABLE}')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'


class TypedVariable(Variable):
    def __init__(self, _type=None, name=None):
        self._type = _type
        Variable.__init__(self, name)

    def get_variable(self):
        return Variable(self.name)

    @classmethod
    def get_temp_variable(cls, _type):
        var = Variable.get_temp_variable()
        return cls(_type=_type, name=var.name)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._type}, {self.name})'


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
