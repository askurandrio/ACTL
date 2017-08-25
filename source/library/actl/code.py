from actl import syntax_opcodes
from .opcodes import AnyOpCode


class Code(AnyOpCode):
    __rules = []

    def __init__(self, code=None):
        self.buff = list(code if code else [])

    def compile(self):
        self.__compile()
        return iter(self)

    def __transform(self):
        for idx in range(len(self.buff)):
            for rule in self.__rules:
                idx_end = rule.match(self.buff[idx:])
                if idx_end is not None:
                    result = rule(self, idx, self.buff[idx:idx+idx_end+1])
                    if (not rule.add_context) and (result is not None):
                        self.buff[idx:idx+idx_end+1] = result
                    return True

    def __after_transform(self):
        for idx, opcode in enumerate(self.buff):
            if syntax_opcodes.Operator.NEXT_LINE_CODE == opcode:
                del self.buff[idx]
                return True

    def __compile(self):
        while self.__transform():
            pass
        while self.__after_transform():
            pass
        self.code = list(self.buff)
        for idx, opcode in enumerate(self.code):
            if syntax_opcodes.AnySyntaxCode == opcode:
                raise RuntimeError(f'Detected object of {syntax_opcodes.AnySyntaxCode} with idx {idx}:\n{self}')

    def __iter__(self):
        return iter(self.code)

    def __repr__(self, ident=4):
        s = ''
        s += 'Code:'
        for opcode in self:
            s += ('\n' + (' ' * ident))
            if isinstance(opcode, self.__class__):
                s += opcode.__repr__(ident + 4)
            else:
                s += repr(opcode)
        return s

    @classmethod
    def add_syntax(cls, *template, add_context=False):
        def temp(func):
            cls.__rules.append(SyntaxRule(func, template, add_context))
            return func
        return temp


class SyntaxRule:
    def __init__(self, func, template, add_context=False):
        self.func = func
        self.template = template
        self.add_context = add_context

    def match(self, buff):
        idx = 0
        for idx, syntax_code in enumerate(self.template):
            if (len(buff) < (idx+1)) or (syntax_code != buff[idx]):
                return None
        return idx

    def __call__(self, code, idx_start, matched_code):
        if self.add_context:
            context = {'code':code, 'idx_start':idx_start}
            return self.func(context=context, *matched_code)
        else:
            return self.func(*matched_code)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.func}, {self.template})'