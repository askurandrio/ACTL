from actl.code import Code, SET


class Translator:
    def __init__(self, code):
        self.code = code

    def translate(self, add_main=True):
        s = ''.join(self.__translate())
        if add_main:
            s += 'void main() {} \n\n'
        return s

    def __translate(self):
        for opcode in self.code:
            if isinstance(opcode, Code):
                yield '{\n'
                yield from self.__class__(opcode).translate(add_main=False)
                yield '}\n'
            elif isinstance(opcode, SET):
                yield f'auto {opcode.name.name} = {opcode.value};\n'
            else:
                raise RuntimeError(opcode)

    @classmethod
    def get_value(cls, value):
        if False:
            pass