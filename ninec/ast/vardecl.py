
from ast.expression import Expression
from ast import declaration
from ast import memberflags

from nine import error
from nine.scope import Scope
from nine import token
from nine.set import *

class VarDecl(declaration.Declaration):
    def __init__(self, name, position, type=None, initializer=None, flags=None):
        assert isinstance(name, basestring), name

        self.name = name
        self.position = position

        self.type = type # May be None, in which case it must be deduced during the semantic phase
        self.initializer = initializer

        self.flags = flags or memberflags.MemberFlags()

        self.builder = None # Unset until code generation time

        assert type is not __builtins__['type']

    def parse(tokens):
        from ast.identifier import Identifier
        from ast import vartypes

        flags = memberflags.MemberFlags()
        oldPos = tokens.getPosition()

        while True:
            tok = tokens.getNext()
            if tok == 'static':
                flags.static = True
            else:
                tokens.unget()
                break

        if tokens.peek() != 'var':
            tokens.setPosition(oldPos)
            return None

        tokens.expect('var')

        name = tokens.getNext()
        if name.type != 'identifier':
            raise error.SyntaxError, 'Expected identifier after keyword "var", got %r' % name

        initializer = None
        type = None

        if tokens.peek() == 'as':
            tokens.getNext() # eat the 'as'

            type = vartypes.Type.parse(tokens)
            if type is None:
                raise error.SyntaxError, 'Expected type after "as".  Got %r' % tokens.peek()

        if tokens.peek() == '=':
            tokens.getNext() # eat the '=' sign
            initializer = Expression.parse(tokens)
            if initializer is None:
                raise error.SyntaxError, 'Expected expression after "=".  Got %r' % tokens.peek()

        peek = tokens.peek()
        if peek not in (token.END_OF_STATEMENT, token.END_OF_FILE):
            raise error.SyntaxError, 'Expected end of statement.  Got %r' % peek

        return VarDecl(name.value, name.position, type, initializer, flags)
    parse = staticmethod(parse)

    def resolveNames(self, scope):
        pass

    def semantic(self, scope):
        from ast import vartypes

        if self.name in scope and scope[self.name] is not self:
            # TODO: better error message, especially if the symbol is already defined, but it an outer scope.
            raise error.SyntaxError, 'Variable declaration "%s" conflicts with %r declared at %r' % (self.name, scope[self.name], scope[self.name].position)

        initializer = self.initializer
        type = self.type

        if type is not None:
            type = type.semantic(scope)

        if initializer is not None:
            initializer = initializer.semantic(scope)

            initializerType = initializer.getType()

            if type is None:
                type = initializerType
            elif type != initializerType:
                raise error.TypeError, 'Cannot initialize variable %s with value %s of type %s, because of declared type %s' % (self.name, initializer, initializerType, type)

        if type is None:
            raise error.SyntaxError(self.position, 'Unable to deduce type of variable "%s"' % self.name)

        if not isinstance(type, vartypes.Type):
            raise error.SyntaxError, 'Declaration of variable %s of type %r is a bit of a problem.  %r is not a type!' % (self.name, type, type)

        if scope.func is not None or scope.parent is not None and scope.klass is None:
            # Note: If a scope has a parent, then the variable is local to that block.
            # This way, block-local variables are not treated as global variables,
            # despite not being declared in any function body.
            decl = _LocalVar(self.name, self.position, type, initializer, flags=self.flags)
        elif scope.klass is not None:
            decl = _MemberVar(self.name, self.position, type, initializer, scope.klass, flags=self.flags)
        else:
            # Variables declared in the root scope are global.
            decl = _GlobalVar(self.name, self.position, type, initializer, flags=self.flags)

        scope[decl.name] = decl
        return decl

    def getType(self):
        return self.type

    def emitCode(self, gen):
        assert False, '%r does not subclass VarDecl.emitCode!' % self

    def emitLoad(self, gen):
        assert False, '%r does not subclass VarDecl.emitLoad!' % self

    def emitLoadAddress(self, gen):
        assert False, '%r does not subclass VarDecl.emitLoadAddress!' % self

    def emitAssign(self, rhs, gen):
        assert False, '%r does not subclass VarDecl.emitAssign!' % self

    def __repr__(self):
        if self.initializer is not None:
            return '<%s %s = %s>' % (type(self).__name__, self.name, self.initializer)
        else:
            return super(VarDecl, self).__repr__()

class _LocalVar(VarDecl):
    def semantic(self, scope):
        return self

    def emitCode(self, gen):
        if self.builder is not None: return

        self.builder = gen.defineLocal(self.type)

        if self.initializer is not None:
            self.emitAssign(self.initializer, gen)

    def emitLoad(self, gen):
        gen.ilGen.Emit(gen.opCodes.Ldloc, self.builder)

    def emitLoadAddress(self, gen):
        gen.ilGen.Emit(gen.opCodes.Ldloca, self.builder)

    def emitAssign(self, rhs, gen):
        from nine import util
        from CLR import System

        object = util.getNineType(System.Object)
        value = util.getNineType(System.ValueType)

        assert self.builder is not None
        rhs.emitLoad(gen)

        if self.type == object and value.isDescendant(rhs.getType()):
            gen.ilGen.Emit(gen.opCodes.Box, rhs.getType().builder)

        gen.ilGen.Emit(gen.opCodes.Stloc, self.builder)

class _GlobalVar(VarDecl):
    def semantic(self, scope):
        return self

    def emitDeclaration(self, gen):
        if self.builder is not None: return

        self.builder = gen.defineGlobal(self.name, self.type)

    def emitCode(self, gen):
        self.emitDeclaration(gen)
        if self.initializer is not None:
            self.emitAssign(self.initializer, gen)

    def emitLoad(self, gen):
        assert self.builder is not None, self
        gen.ilGen.Emit(gen.opCodes.Ldsfld, self.builder)

    def emitLoadAddress(self, gen):
        gen.ilGen.Emit(gen.opCodes.Ldsflda, self.builder)

    def emitAssign(self, rhs, gen):
        from nine import util
        from CLR import System

        object = util.getNineType(System.Object)
        value = util.getNineType(System.ValueType)

        assert self.builder is not None, (self, self.name)

        rhs.emitLoad(gen)

        if self.type == object and value.isDescendant(rhs.getType()):
            gen.ilGen.Emit(gen.opCodes.Box, rhs.getType().builder)

        gen.ilGen.Emit(gen.opCodes.Stsfld, self.builder)

class _MemberVar(VarDecl):
    def __init__(self, name, position, type, initializer, klass, flags):
        super(_MemberVar, self).__init__(name, position, type, initializer, flags)
        self.klass = klass

    def semantic(self, scope):
        return self

    def semantic2(self, scope):
        return self

    def emitDeclaration(self, gen):
        if self.builder is not None: return

        ilType = self.type.builder

        flags = gen.FieldAttributes.Public
        if self.flags.static:
            flags |= gen.FieldAttributes.Static

        self.builder = self.klass.builder.DefineField(self.name, ilType, flags)

    def emitCode(self, gen):
        assert self.initializer is None, 'Initializers on class members are not yet implemented.'
