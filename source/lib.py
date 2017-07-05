class OpCode:
    pass


class SET(OpCode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Parser:
    def __init__(self):
        self.code = []
    
    def parse(self, line):
        if '=' in line:
            name, value = line.split('=')
            self.code.append(SET(name, value))

    @classmethod 
    def parse_file(cls, filename):
        obj = cls()
        for line in open(filename):
            obj.parse(line)
        return obj
     

    