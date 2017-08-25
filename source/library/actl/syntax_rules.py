import actl_types
from actl import opcodes, syntax_opcodes
from .code import Code, SyntaxRule


Code.add_syntax(syntax_opcodes.Word)(lambda word: (opcodes.Variable(name=word.word),))


@Code.add_syntax(syntax_opcodes.Number, add_context=True)
def _(number, context):
    code = context['code']
    var = opcodes.Variable.get_temp_variable()
    code.buff.insert(0, opcodes.DECLARE(opcodes.Variable(actl_types.number),  var))
    code.buff.insert(1, opcodes.SET(var, number.number))
    code.buff.insert(2, syntax_opcodes.Operator.NEXT_LINE_CODE)
    code.buff[context['idx_start'] + 3] = var


@Code.add_syntax(opcodes.Variable, opcodes.Variable)
def _(type, name):
    return (opcodes.DECLARE(type=type, name=name),)



@Code.add_syntax(syntax_opcodes.Operator.OPEN_CODE, add_context=True)
def _(_, context):
    main_code, idx_start = context['code'], context['idx_start']
    count = 1
    code = main_code.__class__()
    while main_code.buff[idx_start:]:
        if main_code.buff[idx_start+1] == syntax_opcodes.Operator.OPEN_CODE:
            count += 1
            code.buff.append(main_code.buff.pop(idx_start+1))
        elif main_code.buff[idx_start+1] == syntax_opcodes.Operator.CLOSE_CODE:
            count -= 1
            if count != 0:
                code.buff.append(main_code.buff.pop(idx_start+1))
            else:
                code.compile()
                main_code.buff.pop(idx_start+1)
                break
        else:
            code.buff.append(main_code.buff.pop(idx_start+1))
    main_code.buff[idx_start] = code
