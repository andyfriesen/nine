
from ast.identifier import Identifier

from nine import error

class DotExpression(object):
    '''Expression of the form functionCallExpression ( "." Identifier )*

    Differs from QualifiedName in that it is an expression.  Type names and the like
    consist only of identifiers, whereas DotExpression is pretty much anything else.
    '''

    def __init__(self, position, lhs, rhs):
        assert isinstance(rhs, Identifier), '%r should be an Identifier, not %s' % (rhs, type(rhs))

        self.position = position
        self.lhs = lhs
        self.rhs = rhs

    def parse(tokens):
        from ast.primitiveexpression import PrimitiveExpression

        lhs = PrimitiveExpression.parse(tokens)

        if lhs is None:
            return None

        if tokens.peek() != '.':
            return lhs

        tokens.expect('.')
        expr = lhs

        while True:
            position = tokens.peek().position

            rhs = Identifier.parse(tokens)

            if rhs is None:
                raise error.SyntaxError, 'Expected identifier, got %r' % tokens.peek()

            expr = DotExpression(position, expr, rhs)

            if tokens.peek() != '.':
                break

            tokens.expect('.')
            continue

        return expr

    parse = staticmethod(parse)

    def semantic(self, scope):
        from ast import vartypes
        from ast.namespace import Namespace
        from ast.qualifiedname import QualifiedName
        from ast.identifier import Identifier
        from ast.memberreference import MemberReference

        lhs = self.lhs.semantic(scope)
        rhs = self.rhs

        assert isinstance(rhs, Identifier), rhs

        #lhs can be a namespace, a class name, or an expression.

        if isinstance(lhs, (Namespace, QualifiedName)):
            return QualifiedName(lhs, rhs).semantic(scope)

        elif isinstance(lhs, vartypes.Type):
            # Static attribute of a class.
            return lhs.getMember(lhs, rhs.name)

        else:
            # Assume expression
            ltype = lhs.getType()
            return ltype.getMember(lhs, rhs.name)

    def __repr__(self):
        return '%r.%r' % (self.lhs, self.rhs)
