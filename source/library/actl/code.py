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
        for idx_buff in range(len(self.buff)):
            for template, add_context, func in self.__rules:
                is_match = True
                idx = 0
                for idx, syntax_code in enumerate(template):
                    if (len(self.buff) < (idx_buff+idx+1)) or (syntax_code != self.buff[idx_buff+idx]):
                        is_match = False
                        break
                if is_match:
                    is_find = True
                    if add_context:
                        context = {'code':self, 'idx_buff':idx_buff}
                        temp = func(context=context, *self.buff[idx_buff:idx_buff+idx+1])
                    else:
                        temp = func(*self.buff[idx_buff:idx_buff+idx+1])
                    self.buff[idx_buff:idx_buff+idx+1] = temp
                    return True

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
            cls.__rules.append((template, add_context, func))
            return func
        return temp


@Code.add_syntax(syntax_opcodes.Operator.OPEN_CODE, add_context=True)
def _(_, context):
    self, idx_buff = context['code'], context['idx_buff']
    count = 1
    code = self.__class__()
    while self.buff[idx_buff:]:
        if self.buff[idx_buff+1] == syntax_opcodes.Operator.OPEN_CODE:
            count += 1
            code.buff.append(self.buff.pop(idx_buff+1))
        elif self.buff[idx_buff+1] == syntax_opcodes.Operator.CLOSE_CODE:
            count -= 1
            if count != 0:
                code.buff.append(self.buff.pop(idx_buff+1))
            else:
                code.compile()
                self.buff.pop(idx_buff+1)
                break
        else:
            code.buff.append(self.buff.pop(idx_buff+1))
    return (code,)


Code.add_syntax(syntax_opcodes.Number)(lambda number: (SET(syntax_opcodes.Name.get_temp_name(), number),))
Code.add_syntax(syntax_opcodes.Name, syntax_opcodes.Operator('='), syntax_opcodes.AnySyntaxCode) \
    (lambda name, _, value: (SET(name, value),))
Code.add_syntax(syntax_opcodes.Operator.NEXT_LINE_CODE)(lambda _: ())
