
class Scope(object):

    def __init__(self, parent, func=None):
        self.parent = parent
        self.func = None
        self.symbols = {}

        self.klass = None # The type of the scope's enclosing class
        self.this = None # A reference to the current object (if applicable)

        if parent is not None:
            self.func = func or parent.func
            self.klass = parent.klass
            self.this = parent.this

    def __getitem__(self, key):
        return self.resolveSymbol(key)

    def __setitem__(self, key, value):
        self.symbols[key] = value

    def __contains__(self, key):
        return self.resolveSymbol(key) is not None

    def addSymbol(self, name, value):
        assert name not in self.symbols
        self.symbols[name] = value

    def resolveSymbol(self, name):
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent is not None:
            return self.parent.resolveSymbol(name)
        else:
            return None
