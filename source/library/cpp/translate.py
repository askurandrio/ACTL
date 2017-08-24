from actl import opcodes
from actl import syntax_opcodes
from actl.code import Code



class Translator:
    def __init__(self, code):
        self.code = code

    def translate(self, ident=0, add_main=True):
        s = ''.join(self.__translate(ident))
        if add_main:
            s += 'int main() {\n    return 0;\n} \n\n'
        return s

    def __translate(self, ident):
        for opcode in self.code:
            if Code == opcode:
                yield (' ' * ident) + '{\n'
                yield from self.__class__(opcode).translate(ident=ident+4, add_main=False)
                yield (' ' * ident) + '}\n'
            elif syntax_opcodes.Word == opcode:
                yield opcode.name
            elif syntax_opcodes.Number == opcode:
                yield opcode.number
            elif opcodes.LOAD_ATTRIBUTE == opcode:
                yield '.'
            else:
                raise RuntimeError(value)
