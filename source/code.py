class MetaOpCode(type):
    rules = []

    def __init__(self, *args, **kwargs):
        self.rules.append(self.rule)
        self.opcode = self.__name__
        type.__init__(self, *args, **kwargs)


class VirtualOpCode:
    def __init__(self, *args):
        self.args = args

    def __repr__(self):
        return f'{self.opcode}{self.args}'


class NEXT_LINE(VirtualOpCode, metaclass=MetaOpCode):
    @classmethod
    def rule(cls, it):
        for token in it:
            if isinstance(token, VirtualOpCode):
                yield token
                continue
            if token == '\n':
                yield cls()
                continue
            yield token


class CONST_STRING(VirtualOpCode, metaclass=MetaOpCode):
    OPEN_STRING_TOKEN = ("'", '"') #Task: add '"""'

    def __init__(self, s):
        super().__init__(str(s))

    @classmethod
    def rule(cls, it):
        for token in it:
            if isinstance(token, VirtualOpCode):
                yield token
                continue
            if token in cls.OPEN_STRING_TOKEN:
                s = None
                for open_string_token in cls.OPEN_STRING_TOKEN:
                    if open_string_token == token:
                        s = ''
                        for token in it:
                            if open_string_token == token:
                                break
                            else:
                                s += token
                        yield cls(s)
                        break
                if s is None:
                    raise RuntimeError('Wrong branch')
                continue
            yield token


class CONST_NUMBER(VirtualOpCode, metaclass=MetaOpCode):
    def __init__(self, number):
        super().__init__(float(number))

    @classmethod
    def rule(cls, it):
        for token in it:
            if isinstance(token, VirtualOpCode):
                yield token
                continue
            if token.isdigit():
                s = token
                for token in it:
                    if (not isinstance(token, VirtualOpCode)) and token.isdigit() or (token == '.'):
                        s += token
                    else:
                        break
                yield cls(s)
                #no continue. yield non-using token
            yield token


class NAME(VirtualOpCode, metaclass=MetaOpCode):
    def __init__(self, name):
        super().__init__(str(name))

    @classmethod
    def rule(cls, it):
        for token in it:
            if isinstance(token, VirtualOpCode):
                yield token
                continue
            if token.isalpha():
                s = token
                for token in it:
                    if not isinstance(token, VirtualOpCode):
                        s += token
                    else:
                        break
                yield cls(s)
                #no continue. yield non-using token
            yield token


class Code(list):
    pass


class Parser:
    def __init__(self, **kwargs):
        self.code = []
        if 'file' in kwargs:
            self.it = open(kwargs['file']).read()
        else:
            raise RuntimeError('Wrong branch')
        self.rules = list(MetaOpCode.rules)

    def parse(self):
        it = self.it
        for rule in self.rules:
            it = rule(it)
        return Code(it)