from ast.passstatement import PassStatement
from ast.assignstatement import AssignStatement
from ast.identifier import Identifier
from ast.vardecl import VarDecl
from ast.vartypes import Type
from ast import memberflags

from nine import error
from nine import token
from nine import util
from nine.codegenerator import CodeGenerator
from nine.scope import Scope
from CLR import System

class EnumChild(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.type = None
        self.builder = None

    def __repr__(self):
        return "<enum %s.%s = %r>" % (self.type.name, self.name, self.value)

    def getType(self):
        return self.type

    def semantic(self, scope):
        assert scope.klass is not None, self
        self.type = scope.klass
        return self

    def emitLoad(self, gen):
        gen.ilGen.Emit(gen.opCodes.Ldc_I4, self.value)

    def emitDeclaration(self, gen):
        assert self.builder is None, self
        self.builder = self.type.builder.DefineLiteral(self.name, self.value)


class EnumBody(object):
    def __init__(self, decls):
        self.decls = decls

    def parse(tokens):
        if tokens.peek() is not token.BEGIN_BLOCK:
            return None

        decls = []

        tokens.expect(token.BEGIN_BLOCK)
        while tokens.peek() is not token.END_BLOCK:
            decl = (
                AssignStatement.parse(tokens) or
                Identifier.parse(tokens) or
                PassStatement.parse(tokens)
            )

            if decl is None:
                raise error.SyntaxError, 'Expected end block, value declaration, or pass statement.  Got %r' % tokens.peek()

            while tokens.peek() is token.END_OF_STATEMENT:
                tokens.getNext()

            if isinstance(decl, PassStatement): continue # Don't store pass statements.  They're not useful.

            decls.append(decl)

        tokens.expect(token.END_BLOCK)

        return EnumBody(decls)
    parse = staticmethod(parse)

    def semantic(self, scope):
        from ast.literalexpression import LiteralExpression
        from ast.identifier import Identifier

        decls = []
        value = 0
        for decl in self.decls:
            name = ''
            if not isinstance(decl, EnumChild):
                if isinstance(decl, AssignStatement):

                    #check to ensure getting assigned only to an int

                    #fixme: will fail if expression is not a literal
                    value = decl.expression.getValue()
                    name = decl.lhs.name
                elif isinstance(decl, Identifier):
                    name = decl.name
                elif isinstance(decl, EnumChild):
                    pass
                else:
                    raise error.SyntaxError('Expected enumerator child, got %r' % decl)
                decl = EnumChild(name, value)
            decl = decl.semantic(scope)
            decls.append(decl)
            scope[decl.name] = decl
            value = value + 1

        return EnumBody(decls)

class EnumDecl(Type):
    def __init__(self, name, body):
        super(EnumDecl, self).__init__(name)
        self.name = name
        self.body =body

    def parse(tokens):
        if tokens.peek() != 'enum':
            return None
        tokens.expect('enum')

        position = tokens.peek().position
        name = tokens.getNext()

        if name.type != 'identifier':
            tokens.unget()
            raise error.SyntaxError(position, 'Expected enumerator name, got %r' % name)

        name = name.value

        tokens.expect(':')
        tokens.expect(token.END_OF_STATEMENT)

        body = EnumBody.parse(tokens)
        if body is None:
            raise error.SyntaxError, 'Expected enumerator body, got %r' % tokens.peek()

        return EnumDecl(name, body)
    parse = staticmethod(parse)

    def semantic(self, scope):
        if scope.symbols.get(self.name, self) is not self:
            raise error.NameError, "A symbol named '%s' already exists in the current scope." % self.name

        scope[self.name] = self

        childScope = Scope(parent=scope)
        childScope.klass = self
        self.body = self.body.semantic(childScope)
        return self

    def getMember(self, this, name):
        if this is self: this = None

        for decl in self.body.decls:
            if decl.name == name:
                return (decl)

        raise error.NameError, "No symbol named '%s' is defined in enumerator %s" % (name, self.name)

    def emitDeclaration(self, gen):
        if self.builder is not None:
            return
        self.builder = gen.module.DefineEnum(self.name, gen.TypeAttributes.Public, util.getNetType(System.Int32))
        for decl in self.body.decls:
            decl.emitDeclaration(gen)

    def emitCode(self, gen):
        self.builder.CreateType()
