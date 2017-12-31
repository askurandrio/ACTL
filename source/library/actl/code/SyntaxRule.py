
class SyntaxRule:
    def __init__(self, func, template):
        self.func = func
        self.template = template


class SyntaxRules:
    def __init__(self):
        self.rules = []

    def add(self, template, func):
        if func is not None:
            self.rules.append(SyntaxRule(func, template))
        def decorator(func):
            if func is None:
                self.rules.append(SyntaxRule(func, template))
            return func
        return decorator
