
from nine import error
from nine.token import Token

class Identifier(object):
    '''An identifier is just a name.

    Identifier has not yet been resolved, it has no idea what it is
    referring *to*.

    When semantic analysis happens, Identifiers do the name resolution,
    returning instead an object which knows more about the subject.
    (such as a VariableExpression, if the Identifier is a reference to a
    variable)
    '''
    def __init__(self, name, position):
        assert isinstance(name, basestring), name
        self.name = name
        self.position = position

    def parse(tokens):
        peek = tokens.getNext()

        if peek.type == 'identifier':
            return Identifier(peek.value, peek.position)

        elif peek.type == 'keyword' and peek.value in ('int', 'float', 'char', 'string', 'boolean', 'void'):
            return Identifier(peek.value, peek.position)

        else:
            tokens.unget()
            return None

    parse = staticmethod(parse)

    def semantic(self, scope):
        from ast import vartypes
        from ast.vardecl import VarDecl
        from ast.variableexpression import VariableExpression
        from ast.namespace import Namespace

        from nine import lexer
        if self.name in lexer.KEYWORDS:
            v = self.name
            if v == 'float':
                return vartypes.FloatType
            elif v == 'int':
                return vartypes.IntType
            elif v == 'char':
                return vartypes.CharType
            elif v == 'string':
                return vartypes.StringType
            elif v == 'boolean':
                return vartypes.BooleanType
            elif v == 'void':
                return vartypes.VoidType
            else:
                assert False, v

        # Get the symbol to which the name refers, then return the appropriate
        # structure depending on what its type is.
        sym = scope.resolveSymbol(self.name)
        
        if sym is None:
            raise error.NameError(self.position, 'Symbol "%s" is not defined' % self.name)

        elif isinstance(sym, VarDecl):
            return VariableExpression(Token(self.name, 'identifier', *self.position), sym)

        else:
            # Assume that the symbol we fetched is precisely what we want.
            return sym

    def getType(self):
        assert False, self

    def emitCode(self, gen):
        assert False, 'Internal badness: asked to emitCode for unresolved symbol %r' % self.name

    def emitLoad(self, gen):
        assert False, 'Internal badness: asked to emitLoad for unresolved symbol %r' % self.name

    def __repr__(self):
        return "<Identifier '%s'>" % self.name
