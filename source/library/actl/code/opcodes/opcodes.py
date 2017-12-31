

from ..parser import Word, Operator
from ..SyntaxRule import SyntaxRules
from .AnyOpCode import AnyOpCode


RULES = SyntaxRules()


def create_opcode(name, *attributes):
	code = 'class {name}(AnyOpCode):' \
			 '   def __init__(self, {args}):'
	code = code.format(name=name, args='.'.join(attributes))
	for attribute in attributes:
		code += f'      self.{attribute} = {attribute}'
	lc_scope = {}
	exec(code, globals(), lc_scope) #pylint: disable=W0122
	return lc_scope[name]


VARIABLE = create_opcode('Variable', 'name')
RULES.add((Word), lambda word: VARIABLE(name=word.word))

SET_VARIABLE = create_opcode('SET_VARIABLE', 'destination', 'source')
RULES.add((VARIABLE, Operator('='), VARIABLE),
			 lambda destination, _, source: SET_VARIABLE(destination, source)) #pylint: disable=C0330
