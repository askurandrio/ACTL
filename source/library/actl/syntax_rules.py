from .code import Code
from actl import syntax_opcodes
from .opcodes import AnyOpCode, SET


Code.add_syntax(syntax_opcodes.Number)(lambda number: (SET(syntax_opcodes.Name.get_temp_name(), number),))
Code.add_syntax(syntax_opcodes.Name, syntax_opcodes.Operator('='), syntax_opcodes.AnySyntaxCode) \
    (lambda name, _, value: (SET(name, value),))
Code.add_syntax(syntax_opcodes.Operator.NEXT_LINE_CODE)(lambda _: ())
Code.add_syntax(syntax_opcodes.Name('def'))(lambda _: ())


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