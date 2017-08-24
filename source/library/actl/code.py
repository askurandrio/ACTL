from actl import syntax_opcodes
from .opcodes import AnyOpCode, SET


class Code(AnyOpCode):
    CODE_OPEN = type('CodeOpen', (), {})()
    CODE_CLOSE = type('CodeClose', (), {})()
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
                    if result is not None:
                        self.buff[idx:idx+idx_end+1] = result
                    return True
        pass

    def __compile(self):
        while self.__transform():
            pass
        self.code = list(self.buff)
        for idx, opcode in enumerate(self.code):
            if syntax_opcodes.AnySyntaxCode == opcode:
                raise RuntimeError(f'Detected object of {syntax_opcodes.AnySyntaxCode} with idx {idx}:\n{self}')
        pass

    def __iter__(self):
        return iter(self.code)

    def __repr__(self, ident=4):
        s = ''
        s += 'Code:'
        for opcode in self:
            s += ('\n' + (' ' * ident))
            if isinstance(opcode, self.__class__):
                s += opcode.__repr__(ident + 4)
            elif isinstance(opcode, syntax_opcodes.AnySyntaxCode):
                s += 'SyntaxCode.' + repr(opcode)
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


@Code.add_syntax(syntax_opcodes.Operator.OPEN_CODE, add_context=True)
def _(_, context):
    self, idx_start = context['code'], context['idx_start']
    count = 1
    code = self.__class__()
    while self.buff[idx_start:]:
        if self.buff[idx_start+1] == syntax_opcodes.Operator.OPEN_CODE:
            count += 1
            code.buff.append(self.buff.pop(idx_start+1))
        elif self.buff[idx_start+1] == syntax_opcodes.Operator.CLOSE_CODE:
            count -= 1
            if count != 0:
                code.buff.append(self.buff.pop(idx_start+1))
            else:
                code.compile()
                self.buff.pop(idx_start+1)
                break
        else:
            code.buff.append(self.buff.pop(idx_start+1))
    return (code,)


Code.add_syntax(syntax_opcodes.Number)(lambda number: (SET(syntax_opcodes.Name.get_temp_name(), number),))
Code.add_syntax(syntax_opcodes.Name, syntax_opcodes.Operator('='), syntax_opcodes.AnySyntaxCode) \
    (lambda name, _, value: (SET(name, value),))
Code.add_syntax(syntax_opcodes.Operator.NEXT_LINE_CODE)(lambda _: ())
Code.add_syntax(syntax_opcodes.Name('def'), )(lambda _: ())

