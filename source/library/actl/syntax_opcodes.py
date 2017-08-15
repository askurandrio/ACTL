import sys

import pyparsing


OPERATORS = '.+-=*/,()[]{{}}=!@'
ALPHAS = ''.join(filter(str.isalpha, map(chr, range(sys.maxunicode + 1))))


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
    COUNT_TEMP_NAME = -1

    def __init__(self, name):
        self.name = name
    
    def __eq__(self, item):
        if isinstance(item, self.__class__):
            return self.name == item.name
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"
    
    @classmethod
    def get_temp_name(cls):
        cls.COUNT_TEMP_NAME += 1
        return cls(f'R{cls.COUNT_TEMP_NAME}')

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
