import actl_types
from actl import opcodes, syntax_opcodes
from .code import Code, SyntaxRule


Code.add_syntax(syntax_opcodes.Number)(lambda number: (actl_types.Number(number.number),))
Code.add_syntax(syntax_opcodes.Word)(lambda word: (opcodes.Variable(name=word.word),))
Code.add_syntax(syntax_opcodes.Operator.NEXT_LINE_CODE)(lambda _: ())
Code.add_syntax(syntax_opcodes.Word('def'))(lambda _: ())


@Code.add_syntax(opcodes.Variable, opcodes.Variable)
def _(_type, name):
    return (opcodes.Variable(_type=_type, name=name),)


@Code.add_syntax(opcodes.AnyVirtualOpCode, syntax_opcodes.Operator('.'), opcodes.AnyVirtualOpCode)
def _(obj, _, attribute):
    return (opcodes.LOAD_ATTRIBUTE(obj, attribute),)


@Code.add_syntax(syntax_opcodes.Word, syntax_opcodes.Operator('='), syntax_opcodes.AnySyntaxCode)
def _(name, _, value):
    return (opcodes.SET(name, value),)


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
