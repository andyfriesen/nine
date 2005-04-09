
from nine.scope import Scope

class Namespace(object):
    def __init__(self, name, contents=None):
        self.name = name
        self.symbols = contents or dict()

    def semantic(self, scope):
        symbols = {}

        newScope = Scope(parent=scope)

        for k, v in self.symbols.iteritems():
            symbols[k] = v.semantic(newScope)

        return Namespace('', symbols)

    def emitCode(self, gen):
        for k, v in self.symbols.iteritems():
            v.emitCode(gen)

    def __repr__(self):
        return '<namespace %s>' % self.name
