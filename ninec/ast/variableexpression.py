
from nine.error import SyntaxError
from nine.token import Token

class VariableExpression(object):
    def __init__(self, token, decl):
        from ast.vardecl import VarDecl

        assert isinstance(token, Token), token
        assert isinstance(decl, VarDecl), decl

        self.token = token
        self.variable = decl

    def semantic(self, scope):
        # Semantic testing has already been done, so just return self.
        # VariableExpressions are created by Identifier.semantic,
        # if an Identifier should discover that it is identifying (heh)
        # a variable.
        return self

    def getType(self):
        assert self.variable is not None, 'Internal badness: asked to retrieve the type of a variable which has not yet been resolved!!'

        return self.variable.type

    def apply(self, args):
        from ast.delegatedecl import DelegateDecl
        from ast.delegatecall import DelegateCall
        
        if isinstance(self.variable.getType(), DelegateDecl):
            return DelegateCall(self.variable, args)

    def emitLoad(self, gen):
        assert self.variable is not None, self

        self.variable.emitLoad(gen)

    def emitLoadAddress(self, gen):
        assert self.variable is not None, self

        self.variable.emitLoadAddress(gen)

    def emitAssign(self, rhs, gen):
        assert self.variable is not None, self
        self.variable.emitAssign(rhs, gen)

    def __repr__(self):
        return repr(self.variable)
