

from ...parser import Word, Operator
from ..SyntaxRule import SyntaxRules
from .AnyOpCode import AnyOpCode


RULES = SyntaxRules()


class DynamicOpCode(AnyOpCode):
	_attributes = ()

	def __init__(self, *args, **kwargs):
		for key, value in zip(self._attributes, args):
			setattr(self, key, value)
		for key, value in kwargs.items():
			assert (not hasattr(self, key)), f'This attribute already exist: {key}, {self}'
			setattr(self, key, value)

	def __repr__(self):
		result = f'{self.__class__.__name__}('
		for key in self._attributes:
			result += f'{key}={getattr(self, key)}, '
		if result[-2:] == ', ':
			result = result[:-2]
		result += ')'
		return result


def create_opcode(name, *attributes):
	code_template = 'class {name}(DynamicOpCode):\n' \
	                '   _attributes = ({attributes},)\n'
	code = code_template.format(name=name,
										 attributes=', '.join(f'"{attribute}"' for attribute in attributes))
	lc_scope = {}
	exec(code, globals(), lc_scope) #pylint: disable=W0122
	return lc_scope[name]


VARIABLE = create_opcode('VARIABLE', 'name')
RULES.add((Word,), lambda word: (VARIABLE(name=word.word),))

SET_VARIABLE = create_opcode('SET_VARIABLE', 'destination', 'source')
RULES.add((VARIABLE, Operator('='), VARIABLE),
			 lambda destination, _, source: (SET_VARIABLE(destination, source),)) #pylint: disable=C0330
