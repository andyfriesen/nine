
from nine import error

class QualifiedName(object):
    def __init__(self, lhs, rhs):
        assert lhs is not None
        assert rhs is not None

        self.lhs = lhs
        self.rhs = rhs

    def parse(tokens):
        from ast.identifier import Identifier

        expr = Identifier.parse(tokens)
        if expr is None:
            raise error.SyntaxError, 'Expected identifier, got %r' % tokens.peek()

        while tokens.peek() == '.':
            tokens.expect('.')
            rhs = Identifier.parse(tokens)
            if rhs is None:
                raise error.SyntaxError, 'Expected identifier after ".", got %r' % tokens.peek()

            expr = QualifiedName(expr, rhs)

        return expr
    parse = staticmethod(parse)

    def semantic(self, scope):
        lhs = self.lhs.semantic(scope)

        from ast.namespace import Namespace
        if hasattr(lhs, 'symbols'):

            if self.rhs.name not in lhs.symbols:
                raise error.NameError, 'Could not find symbol %r in namespace %r' % (self.rhs, lhs)

            return lhs.symbols[self.rhs.name]

        else:
            raise error.SyntaxError, 'Symbol %s is not a namespace.  %s.%s makes no sense!' % (self.lhs, self.lhs, self.rhs)

    def __repr__(self):
        return '%r.%r' % (self.lhs, self.rhs)
