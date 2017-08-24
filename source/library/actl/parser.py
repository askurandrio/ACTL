import pyparsing

from .syntax_opcodes import Operator, Word, Number


pyparsing.ParserElement.setDefaultWhitespaceChars('')


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
                            idx = 0
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
        rules.append(Word.get_parser())
        rules.append(Number.get_parser())
        return rules
