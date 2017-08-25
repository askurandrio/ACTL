

CASTINGS = {}


def To(type):
    def temp(method):
        cls = type(method.__self__)
        CASTINGS.setdefault(cls, {})
        CASTINGS[cls][type] = method
        return method
    return temp
