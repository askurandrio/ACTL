class OpCode:
	def __init__(self, opcode, *args):
		self.opcode = opcode
		self.args = args


class Parser:
	def __init__(self):
		self.code = []
    
    def parse(self, line):
        if '=' in line:
        	self.code.append()

    @classmethod 
    def parse_file(cls, filename):
    	obj = cls()
    	for line in open(filename):
    		obj.parse(line)
    	return obj
     

    