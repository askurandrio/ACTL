import sys

import pyparsing


ALPHAS = ''.join(filter(str.isalpha, map(chr, range(sys.maxunicode + 1))))


class Name:
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"
    
    @classmethod
    def get_parser(cls):
        word = pyparsing.Word(ALPHAS + '_', ALPHAS + '_'+ pyparsing.nums)
        word.setParseAction(lambda tokens: cls(tokens[0]))
        return word


class Number:
    def __init__(self, number):
        self.number = number
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.number})"
    
    @classmethod
    def get_parser(cls):
        word = pyparsing.Word(pyparsing.nums, pyparsing.nums + '.')
        word.setParseAction(lambda tokens: cls(float(tokens[0])))
        return word


class Operator:
    def __init__(self, operator):
        self.operator = operator
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.operator})"
    
    @classmethod
    def get_parser(cls):
        word = pyparsing.Word('.+-=*/,()[]{{}}=')
        word.setParseAction(lambda tokens: cls(tokens[0]))
        return word


class MetaCodeOperator(type):
    def __call__(self, operator=''):
        if operator not in self._objects:
            self._objects[operator] = type.__call__(self, operator)
        return self._objects[operator]

        
class CodeOperator(metaclass=MetaCodeOperator):
    _objects = {}
    OPEN = 'open'
    CLOSE = 'close'
    _SHIFT = '__shift'
    NEXT_LINE = 'next_line'

    def __init__(self, operator=''):
        self.operator = operator

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.operator}')"

    @classmethod
    def get_parsers(cls):
        word = pyparsing.LineEnd().suppress()
        word.setParseAction(lambda _: cls('next_line'))
        yield word

        word = pyparsing.Word(':') + pyparsing.ZeroOrMore(' ')
        word.setParseAction(lambda _: cls('open'))
        yield word

class Parser:
    def __init__(self, buff):
        self.buff = buff
        self.rules = self.__get_rules()

    def __iter__(self):
        yield CodeOperator('open')
        shifts = []
        prev_code = CodeOperator()
        while self.buff:
            for idx, shift in enumerate(shifts):
                if shift == self.buff[:len(shift)]:
                    self.buff = self.buff[len(shift):]
                else:
                    for _ in range(len(shifts[idx:])):
                        yield CodeOperator('close')
                    shifts = shifts[:idx]
            is_find = False
            for rule in self.rules:
                for result, start, end in rule.scanString(self.buff):
                    if start == 0:
                        is_find = True
                        self.buff = self.buff[end:]
                        code = result[0]
                        if CodeOperator('open') is prev_code:
                            shifts.append('')
                            for idx, char in enumerate(self.buff):
                                if char != ' ':
                                    break
                                shifts[-1] += char
                            self.buff = self.buff[idx:]
                        yield code
                        prev_code = code
                    break
            if not is_find:
                raise RuntimeError(self.buff)
        for _ in range(len(shifts)):
            yield CodeOperator('close')
        yield CodeOperator('close')
        assert not self.buff

    def __get_rules(self):
        rules = []
        rules.extend(CodeOperator.get_parsers())
        rules.append(Name.get_parser())
        rules.append(Number.get_parser())
        rules.append(Operator.get_parser())
        return rules
