
from ast.expression import Expression
from ast import vartypes

class ExpressionStatement(object):
    '''A statement that is an expression, nothing more.

    The expression is evaluated, and its value discarded.
    '''

    def __init__(self, expr):
        self.expr = expr

    def parse(tokens):
        expr = Expression.parse(tokens)
        if expr is not None:
            return ExpressionStatement(expr)
        else:
            return None
    parse = staticmethod(parse)

    def semantic(self, scope):
        # Future optimization: determine expressions that have no side effects
        # and no purpose, and eliminate them.
        # eg someFunc() + 42
        # Eliminate the addition because it doesn't go anywhere.

        expr = self.expr.semantic(scope)
        assert expr is not None, (expr, self.expr)
        return ExpressionStatement(expr)

    def emitCode(self, gen):
        self.expr.emitLoad(gen)
        #Hmm, I'll leave these lines here
        #But they don't seem to be good for anything and break Delegate goodness
        #-----
        #if self.expr.getType().builder.FullName != 'System.Void':
        #    gen.ilGen.Emit(gen.opCodes.Pop)

    def __repr__(self):
        return self.expr.__repr__()
