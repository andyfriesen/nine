
from CLR import System

from nine import error
from nine import log
from nine import token

from ast.blockstatement import BlockStatement
from ast import memberflags
from ast import vartypes

from nine.set import *

class FunctionDecl(object):
    def __init__(self, name, position, returnType, params, body, flags=None):
        assert isinstance(name, basestring), name
        self.name = name
        self.position = position

        self.returnType = returnType
        self.params = params
        self.body = body

        self.flags = flags or memberflags.MemberFlags()

        self.klass = None # Enclosing class: set during semantic analysis
        self.builder = None # Set during code generation

    def parse(tokens):
        from ast.parameter import Parameter

        oldPos = tokens.getPosition()
        flags = memberflags.MemberFlags()

        position = tokens.peek().position

        while True:
            tok = tokens.getNext()
            if tok == 'static':
                flags.static = True
            elif tok == 'virtual':
                flags.virtual = True
            elif tok == 'abstract':
                flags.abstract = True
            elif tok == 'override':
                flags.override = True
            elif tok == 'sealed':
                flags.sealed = True
            else:
                tokens.unget()
                break

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
            if peek == ',':
                tokens.expect(',')
                continue

            elif peek == ')':
                break

            else:
                raise error.SyntaxError, "Expected ',' or ')', got %r" % peek

        tokens.expect(')')

        if tokens.peek() == 'as':
            tokens.expect('as')
            returnType = vartypes.Type.parse(tokens)
            if returnType is None:
                raise error.SyntaxError(position, 'Expected return type, got %r' % tokens.peek())
        else:
            returnType = vartypes.VoidType

        if flags.abstract:
            if tokens.peek() == ':':
                raise error.SyntaxError(position, 'Abstract function cannot have definition.')
            tokens.expect(token.END_OF_STATEMENT)
            body = None

        else:
            tokens.expect(':')
            tokens.expect(token.END_OF_STATEMENT)

            body = BlockStatement.parse(tokens)

            if body is None:
                raise error.SyntaxError, 'Expected indented block and function body, got %r' % tokens.peek()

        return FunctionDecl(name.value, name.position, returnType, params, body, flags)
    parse = staticmethod(parse)

    def semantic(self, scope):
        '''Does semantic testing on the function signature and the like.

        It is noteworthy that, unlike most other AST nodes, FunctionDecl
        mutates itself instead of returning a new instance.  This is important
        because other Identifiers may resolve to this symbol.

        If this instance were to be discarded, those links would be broken.
        '''

        # Lots of combinations don't make much sense.  The only one that does is "override sealed".
        flags = self.flags
        if ((flags.static and (flags.virtual or flags.abstract or flags.override or flags.sealed)) or
            (flags.virtual and (flags.abstract or flags.override or flags.sealed)) or
            (flags.abstract and flags.sealed)
        ):
            raise error.SyntaxError(self.position, "Modifier set makes no sense")

        if self.name in scope and scope[self.name] is not self:
            raise error.SyntaxError, 'Function %s duplicate definition %r' % (self.name, scope[self.name])

        scope[self.name] = self

        params = []
        for param in self.params:
            params.append(param.semantic(scope))

        self.params = params
        self.returnType = self.returnType.semantic(scope)

        self.klass = scope.klass

        if self.klass is None:
            # Most modifiers make no sense for global functions.
            for f in self.flags:
                if f in ('static', 'virtual', 'abstract', 'override', 'sealed'):
                    raise error.SyntaxError(self.position, 'Modifier %s makes no sense for global function %s' % (f, self.name))

        else:
            self.__checkOverride(scope)
            if self.name == 'ctor':
                from ast import ctor
                return ctor.Ctor(self.position, self.params, self.body, self.flags).semantic(scope)


        return self

    def __checkOverride(self, scope):
        argTypes = [param.type for param in self.params]

        # Which classes define methods with the same name, return type, and arguments?
        baseMethod = self.klass.baseClass.getMethod(self.name, argTypes, self.returnType)

        # If there are any, demand the override keyword, and demand that the base method is not sealed or static.
        if baseMethod is not None:
            baseClass = baseMethod.klass
            if not self.flags.override:
                raise error.OverrideError(self.position, "Method %s overrides %s.%s but is not 'override'" % (self.name, baseClass.name, self.name))

            if baseMethod.flags.sealed or baseMethod.flags.static or not (baseMethod.flags.abstract or baseMethod.flags.virtual):
                raise error.OverrideError(self.position, "Static, sealed, or nonvirtual method %s.%s cannot be overridden" % (baseClass.name, self.name))

        # If not, make sure the override keyword is not present.
        else:
            if self.flags.override:
                raise error.OverrideError(self.position, "Method %s.%s does not override any base class method" % (self.klass.name, self.name))

        # Check for implementation of interface methods
        for iface in self.klass.baseInterfaces:
            ifaceMethod = iface.getMethod(self.name, argTypes, self.returnType)

            if ifaceMethod is not None:
                self.flags.virtual = True
                self.flags.newslot = True # FIXME: this offends me.

    def semantic2(self, scope):
        from nine.scope import Scope

        localScope = Scope(parent=scope, func=self)

        # Fill local scope with function parameters.

        # Local 0 is 'self'
        if self.klass and not self.flags.static:
            index = 1
        else:
            index = 0

        for param in self.params:
            param.index = index
            localScope[param.name] = param
            index += 1

        if not self.flags.abstract:
            assert self.body is not None, (self.name, self.flags)
            body = self.body.semantic(localScope)

        else:
            assert self.body is None
            body = self.body

        self.body = body
        return self

    def emitDeclaration(self, gen):
        from CLR import System

        if self.builder is not None: return

        log.write('emit', 'emitDeclaration func ', self, self.name, self.flags)

        params = System.Array.CreateInstance(System.Type, len(self.params))

        for index, param in enumerate(self.params):
            type = param.type
            assert type is not None, "Internal error: type deduction isn't quite there yet."
            assert type.builder is not None
            params[index] = type.builder

        flagMap = {
            'static' : gen.MethodAttributes.Static,
            'virtual' : gen.MethodAttributes.Virtual,
            'override' : gen.MethodAttributes.Virtual,
            'abstract' : gen.MethodAttributes.Abstract | gen.MethodAttributes.Virtual,
            'sealed' : gen.MethodAttributes.Final,

            'newslot' : gen.MethodAttributes.NewSlot, # TODO: eradicate
        }

        flags = gen.MethodAttributes.Public

        for flag in self.flags:
            flags |= flagMap[flag]

        if self.klass is None:
            flags |= gen.MethodAttributes.Static

        self.builder = gen.typeBuilder.DefineMethod(
            self.name,
            flags,
            self.returnType.builder,
            params
        )
        
    def getType(self):
        return self.returnType

    def emitCode(self, gen):
        from nine.codegenerator import CodeGenerator

        log.write('emit', 'emitCode func', self, self.name)

        assert self.builder is not None, (self, self.name, self.klass)

        subGen = CodeGenerator(gen)
        subGen.ilGen = self.builder.GetILGenerator()
        subGen.methodBuilder = self.builder

        if not self.flags.abstract:
            self.body.emitCode(subGen)
            subGen.ilGen.Emit(subGen.opCodes.Ret)
