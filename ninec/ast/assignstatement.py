
from ast.expression import Expression
from nine.lexer import AssignOperators
from nine import error

from ast.shiftexpression import ShiftExpression
from ast.multiplyexpression import MultiplyExpression
from ast.addexpression import AddExpression
from ast.bitwiseexpression import BitwiseExpression

class AssignStatement(object):
    def __init__(self, lhs, expression):
        self.lhs = lhs
        self.expression = expression

    def parse(tokens):
        from ast.expression import Expression

        pos = tokens.getPosition()

        lhs = Expression.parse(tokens)

        t = tokens.getNext()
        if t not in AssignOperators:
            tokens.setPosition(pos)
            return None

        rhs = Expression.parse(tokens)
        if rhs is None:
            raise error.SyntaxError, 'Expected an expression, got %s' % tokens.peek()

        if t == '=':
            expression = rhs
        elif t.value.endswith('='):
            t.value = t.value[0:len(t.value)-1]
            if t == '<<' or t == '>>' or t == '>>>':
                expression = ShiftExpression(lhs, rhs, t)
            elif t == '*' or t == '/' or t == '%':
                expression = MultiplyExpression(lhs, rhs, t)
            elif t == '+' or t == '-':
                expression = AddExpression(lhs, rhs, t)
            elif t == '&' or t == '|' or t == '^':
                expression = BitwiseExpression(lhs, rhs, t)
            else:
                raise error.SyntaxError, 'Unrecognized assign operator %s=' % t
        else:
            raise error.SyntaxError, 'Everything has gone to shit'

        return AssignStatement(lhs, expression)
    parse = staticmethod(parse)

    def semantic(self, scope):
        lhs = self.lhs.semantic(scope)
        rhs = self.expression.semantic(scope)

        if not hasattr(lhs, 'emitAssign'):
            raise error.TypeError, 'Expression %r cannot be the left-hand-side of an assignment.' % (lhs)

        from ast.identifier import Identifier
        assert not isinstance(lhs, Identifier), (lhs, rhs)
        assert not isinstance(rhs, Identifier), (lhs, rhs)

        ltype = lhs.getType()
        rtype = rhs.getType()

        # TODO: if ltype is None: lhs.setType(rtype) or whatever

        if ltype != rtype and not ltype.isDescendant(rtype):
            raise error.TypeError, 'Cannot convert expression %s of type %s to %s' % (rhs, rtype, ltype)

        return AssignStatement(lhs, rhs)

    def emitCode(self, gen):
        self.lhs.emitAssign(self.expression, gen)

    def __repr__(self):
        return '<Assign %r = %r>' % (self.lhs, self.expression.__repr__())
