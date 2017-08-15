import sys

import pyparsing


OPERATORS = '.+-=*/,()[]{{}}=!@'
ALPHAS = ''.join(filter(str.isalpha, map(chr, range(sys.maxunicode + 1))))
pyparsing.ParserElement.setDefaultWhitespaceChars(' ')


class MetaSyntaxCode(type):
    def __eq__(self, item):
        return isinstance(item, self) or (isinstance(item, type) and issubclass(self, item))
    
    def __ne__(self, item):
        return not (self == item)


class AnySyntaxCode(metaclass=MetaSyntaxCode):
    def __init__(self):
        pass

    def __eq__(self, item):
        return isinstance(item, self.__class__)
    
    def __ne__(self, item):
        return not (self == item)


class Name(AnySyntaxCode, metaclass=MetaSyntaxCode):
    def __init__(self, name):
        self.name = name
    
    def __eq__(self, item):
        if isinstance(item, self.__class__):
            return self.name == item.name
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"
    
    @classmethod
    def get_parser(cls):
        word = pyparsing.Word(ALPHAS + '_', ALPHAS + '_'+ pyparsing.nums)
        word.setParseAction(lambda tokens: cls(tokens[0]))
        return word


class Number(AnySyntaxCode, metaclass=MetaSyntaxCode):
    def __init__(self, number):
        self.number = number
    
    def __eq__(self, item):
        if isinstance(item, self.__class__):
            return self.number == item.number
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}({self.number})"
    
    @classmethod
    def get_parser(cls):
        word = pyparsing.Word(pyparsing.nums, pyparsing.nums + '.')
        word.setParseAction(lambda tokens: cls(float(tokens[0])))
        return word


class Operator(AnySyntaxCode, metaclass=MetaSyntaxCode):
    def __init__(self, operator):
        self.operator = operator

    def __eq__(self, item):
        if isinstance(item, self.__class__):
            return self.operator == item.operator
        return False
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.operator})"
    
    @classmethod
    def get_parsers(cls):
        word = pyparsing.LineEnd().suppress()
        word.setParseAction(lambda _: cls.NEXT_LINE_CODE)
        yield word

        word = pyparsing.Word(':')
        word.setParseAction(lambda _: cls.OPEN_CODE)
        yield word

        word = pyparsing.Word(OPERATORS)
        word.setParseAction(lambda tokens: cls(tokens[0]))
        yield word


Operator.EMPTY = Operator(None)
Operator.OPEN_CODE = Operator('open_code')
Operator.CLOSE_CODE =  Operator('close_code')
Operator.NEXT_LINE_CODE =  Operator('next_line_code')


class Parser:
    def __init__(self, buff):
        self.buff = buff
        self.rules = self.__get_rules()

    def __iter__(self):
        yield Operator.OPEN_CODE
        shifts = []
        prev_code = Operator.EMPTY
        while self.buff:
            if Operator.NEXT_LINE_CODE is prev_code:
                for idx, shift in enumerate(shifts):
                    if shift == self.buff[:len(shift)]:
                        self.buff = self.buff[len(shift):]
                    else:
                        for _ in range(len(shifts[idx:])):
                            yield Operator.CLOSE_CODE
                        shifts = shifts[:idx]
                assert self.buff[0] != ' '
            is_find = False
            for rule in self.rules:
                for result, start, end in rule.scanString(self.buff):
                    if not self.buff[:start].lstrip():
                        is_find = True
                        self.buff = self.buff[end:]
                        code = result[0]
                        if Operator.OPEN_CODE is prev_code:
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
            yield Operator.CLOSE_CODE
        yield Operator.CLOSE_CODE
        assert not self.buff

    def __get_rules(self):
        rules = []
        rules.extend(Operator.get_parsers())
        rules.append(Name.get_parser())
        rules.append(Number.get_parser())
        return rules
