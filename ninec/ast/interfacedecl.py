
from CLR import System

from ast.functiondecl import FunctionDecl
from ast.memberflags import MemberFlags
from ast.passstatement import PassStatement
from ast.qualifiedname import QualifiedName
from ast import vartypes

from nine import error
from nine import log
from nine.scope import Scope
from nine import token
from nine import util

class FunctionPrototype(FunctionDecl):
    def __init__(self, position, name, params, returnType):
        super(FunctionPrototype, self).__init__(
            name, position, returnType, params, body=None, flags=MemberFlags(virtual=True, abstract=True)
        )

    def parse(tokens):
        from ast.parameter import Parameter

        oldPos = tokens.getPosition()

        position = tokens.peek().position

        if tokens.peek() != 'def':
            tokens.setPosition(oldPos)
            return None

        tokens.getNext()

        name = tokens.getNext()
        if name.type != 'identifier':
            raise error.SyntaxError, 'Expected function name, got %r' % name

        tokens.expect('(')

        # parameters
        params = []
        while True:
            param = Parameter.parse(tokens)
            if param is not None:
                params.append(param)

            peek = tokens.peek()
            if peek == ')':
                break

            else:
                tokens.expect(',')

        tokens.expect(')')

        if tokens.peek() == 'as':
            tokens.expect('as')
            returnType = vartypes.Type.parse(tokens)
            if returnType is None:
                raise error.SyntaxError(position, 'Expected return type, got %r' % tokens.peek())
        else:
            returnType = vartypes.VoidType

        if tokens.peek() == ':':
            raise error.SyntaxError(position, 'Interface function cannot have definition.')

        tokens.expect(token.END_OF_STATEMENT)
        body = None

        return FunctionPrototype(position, name.value, params, returnType)
    parse = staticmethod(parse)

    def semantic(self, scope):
        if self.name in scope and scope[self.name] is not self:
            raise error.NameError(self.position, 'A symbol named %s already exists at %r' % scope[self.name].position)

        for index, param in enumerate(self.params):
            self.params[index].type = param.type.semantic(scope)

        self.returnType = self.returnType.semantic(scope)

        return self

    def emitDeclaration(self, gen):
        if self.builder is not None: return

        flags = gen.MethodAttributes.Public | gen.MethodAttributes.Abstract | gen.MethodAttributes.Virtual

        paramTypes = util.toTypedArray(System.Type, [param.type.builder for param in self.params])

        self.builder = gen.typeBuilder.DefineMethod(self.name, flags, self.returnType.builder, paramTypes)

    def emitCode(self, gen):
        pass

class InterfaceBody(object):
    def __init__(self, decls):
        self.decls = decls

    def parse(tokens):
        position = tokens.peek().position

        tokens.expect(token.BEGIN_BLOCK)

        decls = []

        while tokens.peek() is not token.END_BLOCK:
            decl = (
                FunctionPrototype.parse(tokens) or
                PassStatement.parse(tokens)
            )

            if decl is None:
                raise error.SyntaxError, 'Expected end block, variable or class declaration, or pass statement.  Got %r' % tokens.peek()

            while tokens.peek() is token.END_OF_STATEMENT:
                tokens.getNext()

            if isinstance(decl, PassStatement): continue # Don't store pass statements.  They're not useful.

            decls.append(decl)

        tokens.expect(token.END_BLOCK)

        return InterfaceBody(decls)
    parse = staticmethod(parse)

    def semantic(self, scope):
        decls = []

        for stmt in self.decls:
            decls.append(stmt.semantic(scope))

        return InterfaceBody(decls)

    def semantic2(self, scope):
        decls = []

        for stmt in self.decls:
            if hasattr(stmt, 'semantic2'):
                stmt = stmt.semantic2(scope)

            decls.append(stmt)

        return InterfaceBody(decls)

class InterfaceDecl(vartypes.Type):
    def __init__(self, position, name, bases, body):
        super(InterfaceDecl, self).__init__(name)
        self.position = position
        self.name = name
        self.bases = bases
        self.body = body

        self.__emitDecls = False

    def parse(tokens):
        if tokens.peek() != 'interface':
            return None

        position = tokens.peek().position

        tokens.expect('interface')

        name = tokens.getNext()
        if name.type != 'identifier':
            tokens.unget()
            raise error.SyntaxError(position, 'Expected interface name, got %r' % name)

        bases = []

        if tokens.peek() == '(':
            tokens.expect('(')

            while True:
                base = QualifiedName.parse(tokens)
                if base is None:
                    raise error.SyntaxError(position, 'Expected base interface, got %r' % tokens.peek())

                bases.append(base)

                if tokens.peek() == ')':
                    break
                else:
                    tokens.expect(',')

            tokens.expect(')')

        tokens.expect(':')
        tokens.expect(token.END_OF_STATEMENT)

        body = InterfaceBody.parse(tokens)
        if body is None:
            raise error.SyntaxError(position, 'Expected interface body, got %r' % tokens.peek())

        return InterfaceDecl(position, name.value, bases, body)

    parse = staticmethod(parse)

    def semantic(self, scope):
        childScope = Scope(parent=scope)
        childScope.klass = self

        self.body = self.body.semantic(childScope)

        return self

    def semantic2(self, scope):
        childScope = Scope(parent=scope)
        childScope.klass = self

        self.body = self.body.semantic2(childScope)

        return self

    def getMember(self, this, name):
        from ast import classdecl

        for decl in self.body.decls:
            if decl.name == name:
                return classdecl._MethodReference(decl, this)

    def getMethod(self, name, paramTypes, returnType):
        for decl in self.body.decls:
            if decl.name != name: continue
            if decl.returnType != returnType: continue

            pt = [param.type for param in decl.params]

            if pt != paramTypes: continue

            return decl

        else:
            return None

    def emitType(self, gen):
        if self.builder is not None: return

        log.write('emit', 'emitType iface ', self, self.name)

        flags = gen.TypeAttributes.Interface | gen.TypeAttributes.Abstract | gen.TypeAttributes.Public

        ifaces = util.toTypedArray(System.Type, [iface.builder for iface in self.bases])

        self.builder = gen.module.DefineType(self.name, flags, None, ifaces)

    def emitDeclaration(self, gen):
        from nine.codegenerator import CodeGenerator

        if self.__emitDecls: return
        self.__emitDecls = True

        log.write('emit', 'emitDeclaration iface ', self, self.name)

        subGen = CodeGenerator(gen)
        subGen.typeBuilder = self.builder

        for decl in self.body.decls:
            decl.emitDeclaration(subGen)

    def emitCode(self, gen):
        log.write('emit', 'emitType iface ', self, self.name)
        # Interfaces have no method implementations, so just bake it.
        self.builder.CreateType()
