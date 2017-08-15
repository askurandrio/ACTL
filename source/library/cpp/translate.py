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
            elif opcodes.SET == opcode:
                name = self.get_value(opcode.name)
                value = self.get_value(opcode.value)
                yield (' ' * ident) + f'auto {name} = {value};\n'
            else:
                raise RuntimeError(opcode)

    @classmethod
    def get_value(cls, value):
        if syntax_opcodes.Name == value:
            return value.name
        elif syntax_opcodes.Number:
            return value.number
