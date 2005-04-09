import vartypes
from ast.logicalexpression import LogicalExpression
from nine import error

class ParenthExpression(object):
    def __init__(self, childExpression):
        self.childExpression = childExpression
        self.position = (0,"'<fixme: parenthExpression doesn't get position>")

    def parse(tokens):
        position = tokens.peek().position

        if tokens.peek() != '(':
            return None
        tokens.expect('(')

        childExpression = LogicalExpression.parse(tokens)
        if childExpression is None:
            raise error.SyntaxError(position, 'Expected expression, got %r' % tokens.peek())

        if tokens.peek() != ')':
            raise error.SyntaxError, "Expected ')', got %r" % tokens.peek()
        tokens.getNext()

        return ParenthExpression(childExpression)

    parse = staticmethod(parse)

    def getType(self):
        return self.childExpression.getType()

    def semantic(self, scope):
        child = self.childExpression.semantic(scope)
        return ParenthExpression(child)

    def emitLoad(self, gen):
        self.childExpression.emitLoad(gen)

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.childExpression)
