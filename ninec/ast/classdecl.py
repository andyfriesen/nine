
from ast.declaration import Declaration
from ast.functiondecl import FunctionDecl
from ast.passstatement import PassStatement
from ast.vardecl import VarDecl
from ast.vartypes import Type
from ast import memberflags

from nine import error
from nine import log
from nine import token
from nine import util
from nine.codegenerator import CodeGenerator
from nine.scope import Scope

class ClassBody(object):
    def __init__(self, decls):
        self.decls = decls

    def parse(tokens):
        if tokens.peek() is not token.BEGIN_BLOCK:
            return None

        decls = []

        tokens.expect(token.BEGIN_BLOCK)
        while tokens.peek() is not token.END_BLOCK:
            decl = (
                FunctionDecl.parse(tokens) or
                VarDecl.parse(tokens) or
                PassStatement.parse(tokens)
            )

            if decl is None:
                raise error.SyntaxError(tokens.peek().position, 'Expected end block, variable or class declaration, or pass statement.  Got %r' % tokens.peek())

            while tokens.peek() is token.END_OF_STATEMENT:
                tokens.getNext()

            if isinstance(decl, PassStatement): continue # Don't store pass statements.  They're not useful.

            decls.append(decl)

        tokens.expect(token.END_BLOCK)

        return ClassBody(decls)
    parse = staticmethod(parse)

    def semantic(self, scope):
        childScope = Scope(parent=scope)

        decls = []
        for decl in self.decls:
            decls.append(decl.semantic(childScope))

        return ClassBody(decls)

    def semantic2(self, scope):
        childScope = Scope(parent=scope)

        decls = []
        for decl in self.decls:
            decls.append(decl.semantic2(childScope))

        return ClassBody(decls)

class ClassDecl(Declaration, Type):
    def __init__(self, position, name, bases, body, flags):
        super(ClassDecl, self).__init__(name)

        self.position = position
        self.name = name

        self.bases = bases # all supertypes

        # Base class and interfaces.  Worked out during semantic testing
        self.baseClass = None
        self.baseInterfaces = []

        self.body = body

        self.flags = flags

        self.__wasChecked = False # used by semantic() so it's only done once
        self.__declsBuilt = False # Used by emitDeclaration to know if it's been called already or not.

    def parse(tokens):
        flags = memberflags.MemberFlags()
        position = tokens.peek().position

        oldPosition = tokens.getPosition()

        while True:
            tok = tokens.getNext()
            if tok == 'abstract':
                flags.abstract = True
            elif tok == 'sealed':
                flags.sealed = True
            else:
                tokens.unget()
                break

        if tokens.peek() != 'class':
            tokens.setPosition(oldPosition)
            return None
        tokens.expect('class')

        name = tokens.getNext()
        if name.type != 'identifier':
            tokens.unget()
            raise error.SyntaxError(position, 'Expected class name, got %r' % name)

        bases = []

        if tokens.peek() == '(':
            tokens.expect('(')
            # parse base classes
            while tokens.peek() != ')':
                base = Type.parse(tokens)
                if base is None:
                    raise error.SyntaxError(tokens.peek().position, 'Expected type, got %r' % tokens.peek())

                bases.append(base)

                if tokens.peek() == ',':
                    tokens.expect(',')
                else:
                    tokens.expect(')')
                    break

        assert tokens.peek() != '(', 'Internal error at %r: Inheritance is NYI' % tokens.peek()

        tokens.expect(':')
        tokens.expect(token.END_OF_STATEMENT)

        body = ClassBody.parse(tokens)
        if body is None:
            raise error.SyntaxError, 'Expected class body, got %r' % tokens.peek()

        return ClassDecl(position, name.value, bases, body, flags)
    parse = staticmethod(parse)

    def __checkBases(self, scope):
        '''If the object doesn't explicitly extend a class, make sure it
        extends System.Object.

        Also checks various miscellany with respect to base classes, such as
        circular inheritance chains, and inheriting things which are not
        interfaces or classes.
        '''
        from CLR import System

        from ast.interfacedecl import InterfaceDecl

        for index, base in enumerate(self.bases):
            self.bases[index] = base.semantic(scope)

        if 0:
            for base in self.bases:
                print 'BASE', `base`, '\t', `getattr(base, 'bases', None)`

        Object = util.getNineType(System.Object)

        for base in self.bases:
            if isinstance(base, ClassDecl):
                if self.baseClass is None:
                    self.baseClass = base

                elif self.baseClass is not base:
                    raise error.OverrideError(self.position, 'Multiple class inheritance is not yet supported')

                if base.isSubClass(self):
                    raise error.CircularInheritanceError(self.position, 'Circular inheritance between "%s" and "%s"' % (self.name, base.name))

            elif isinstance(base, InterfaceDecl):
                self.baseInterfaces.append(base)

            else:
                raise error.OverrideError(self.position, 'Cannot inherit %r, it is not a class or interface' % base)

        if self.baseClass is None:
            self.baseClass = Object
            self.bases.insert(0, Object)

        if self.baseClass.flags.sealed:
            raise error.OverrideError(self.position, 'Class %s is sealed and cannot be inherited' % base.name)

    def __checkConcreteness(self, scope):
        '''Check that the class implement everything it promises to.
        '''
        if self.flags.abstract: return # abstract classes don't need to implement everything; that's what subclasses are for

        for base in self.bases:
            if 0 and base.external:
                raise error.InternalError("FIXME: __checkConcreteness doesn't work so well with external types")
                continue

            for decl in base.getMethods():
                if not decl.flags.abstract: continue

                paramTypes = [param.type for param in decl.params]
                if self.getMethod(decl.name, paramTypes, decl.returnType) is decl:
                    raise error.OverrideError(self.position, 'Class %s does not implement abstract method %s.%s' % (self.name, base.name, decl.name))

    def resolveNames(self, scope):
        from ast.identifier import Identifier
        from ast.declaration import Declaration

        bases = list()
        for baseClass in self.bases:
            assert not isinstance(baseClass, Declaration), (self, baseClass)
            bases.append(baseClass.semantic(scope))

        self.bases = bases

    def semantic(self, scope):
        # HACK: check scope.symbols directly, because we do not care if outer
        # scopes have a symbol with the same name, only if two symbols have
        # the same name, and are at the same level.

        if self.__wasChecked: return self
        self.__wasChecked = True

        if scope.symbols.get(self.name, self) is not self:
            raise error.NameError, "A symbol named '%s' already exists in the current scope." % self.name

        scope[self.name] = self

        self.__checkBases(scope)
        self.__checkConcreteness(scope)

        childScope = Scope(parent=scope)
        childScope.klass = self

        # If the class has no constructors, define a default ctor
        from ast.ctor import Ctor, DefaultCtor
        hasCtor = bool([d for d in self.body.decls if isinstance(d, Ctor)])

        if not hasCtor:
            self.body.decls.append(DefaultCtor())

        self.body = self.body.semantic(childScope)

        return self

    def semantic2(self, scope):
        childScope = Scope(parent=scope)
        childScope.klass = self

        self.body = self.body.semantic2(childScope)
        return self

    def getMember(self, this, name):
        if this is self: this = None

        for decl in self.body.decls:
            if decl.name != name: continue

            if isinstance(decl, VarDecl):
                return _MemberReference(decl, this)
            elif isinstance(decl, FunctionDecl):
                return _MethodReference(decl, this)
            else:
                assert False, (self, this, name, decl)

        raise error.NameError, "No symbol named '%s' is defined in class %s" % (name, self.name)

    def getCtor(self, params):
        '''Returns a constructor that recieves the given set of parameters.

        params is a list that contains the types that the returned constructor
        recieves.

        (types, not Parameter instances!)
        '''
        from ast.ctor import Ctor

        for decl in self.body.decls:
            if isinstance(decl, Ctor):
                ctorParams = [param.getType() for param in decl.params]
                callingParams = [param.getType() for param in params]

                if ctorParams == callingParams:
                    return decl

        else:
            return None

    def getMethod(self, name, paramList, returnType):
        from ast.functiondecl import FunctionDecl
        from CLR import System

        for decl in self.body.decls:
            if decl.name != name or not isinstance(decl, FunctionDecl): continue

            # compare argument lists
            for param, arg in zip(decl.params, paramList):
                atype = arg.getType()
                ptype = param.getType()

                if atype != ptype:
                    return None

            # compare return types
            returnType = util.getNineType(returnType)
            if returnType != decl.returnType:
                return None

            return decl

        else:
            for base in self.bases:
                m = base.getMethod(name, paramList, returnType)
                if m is not None:
                    return m

        return None

    def getMethods(self):
        '''Returns all methods defined in this class.
        Does not search subclasses.
        '''
        result = []
        for decl in self.body.decls:
            if isinstance(decl, FunctionDecl):
                result.append(decl)
        return result

    def apply(self, args):
        from ast.ctorcall import CtorCall
        return CtorCall(self, args)

    def emitType(self, gen):
        # Redundant calls to emitType have no effect.
        if self.builder is not None: return

        log.write('emit', 'emitType class ', self, self.name)

        from CLR import System

        flags = gen.TypeAttributes.Public

        if self.flags.abstract:
            flags |= gen.TypeAttributes.Abstract
        if self.flags.sealed:
            flags |= gen.TypeAttributes.Sealed

        # Be sure everybody gets their builders built.
        self.baseClass.emitType(gen)
        for iface in self.baseInterfaces:
            iface.emitType(gen)

        ifaces = util.toTypedArray(System.Type, [iface.builder for iface in self.baseInterfaces])

        assert self.baseClass is not None, self
        assert self.baseClass.builder is not None, self.baseClass
        assert None not in ifaces, self.baseInterfaces

        self.builder = gen.module.DefineType(self.name, flags, self.baseClass.builder, ifaces)

    def emitDeclaration(self, gen):
        if self.__declsBuilt: return
        self.__declsBuilt = True

        log.write('emit', 'emitDeclaration class ', self, self.name)

        # Be sure base classes get their stuff done before us.
        self.baseClass.emitDeclaration(gen)
        for iface in self.baseInterfaces:
            iface.emitDeclaration(gen)

        subGen = CodeGenerator(gen)
        subGen.typeBuilder = self.builder

        for decl in self.body.decls:
            decl.emitDeclaration(subGen)

    def emitCode(self, gen):
        log.write('emit', 'emitCode class ', self, self.name)

        subGen = CodeGenerator(gen)
        subGen.typeBuilder = self.builder

        for decl in self.body.decls:
            decl.emitCode(subGen)

        self.builder.CreateType()

    def __eq__(self, rhs):
        return self is rhs

    def __neq__(self, rhs):
        return not (self == rhs)

class _MemberReference(object):
    def __init__(self, decl, this):
        self.decl = decl
        self.this = this

    def semantic(self, scope):
        return self

    def getType(self):
        return self.decl.type

    def emitLoad(self, gen):
        if not self.decl.flags.static:
            assert self.this is not None, self
            self.this.emitLoad(gen)
            gen.ilGen.Emit(gen.opCodes.Ldfld, self.decl.builder)

        else:
            gen.ilGen.Emit(gen.opCodes.Ldsfld, self.decl.builder)

    def emitLoadAddress(self, gen):
        if not self.decl.flags.static:
            assert self.this is not None, self
            self.this.emitLoad(gen)
            gen.ilGen.Emit(gen.opCodes.Ldflda, self.decl.builder)

        else:
            gen.ilGen.Emit(gen.opCodes.Ldsflda, self.decl.builder)

    def emitAssign(self, rhs, gen):
        if not self.decl.flags.static:
            assert self.this is not None
            self.this.emitLoad(gen)
            rhs.emitLoad(gen)
            gen.ilGen.Emit(gen.opCodes.Stfld, self.decl.builder)

        else:
            rhs.emitLoad(gen)
            gen.ilGen.Emit(gen.opCodes.Stsfld, self.decl.builder)

    def __repr__(self):
        return '%r . %r' % (self.this, self.decl.name)

class _MethodReference(object):
    def __init__(self, decl, this):
        self.decl = decl
        self.this = this

    def apply(self, args):
        return _MethodCall(self.decl, self.this, args)

class _MethodCall(object):
    def __init__(self, decl, this, args):
        self.decl = decl
        self.this = this
        self.args = args

    def semantic(self, scope):
        args = []
        for arg in self.args:
            args.append(arg.semantic(scope))

        if self.this is None and not self.decl.flags.static:
            raise error.SyntaxError('Function %s.%s needs self' % (self.decl.klass.name, self.decl.name))

        this = self.this
        if this is not None:
            this = self.this.semantic(scope)

        return _MethodCall(self.decl, this, args)

    def getType(self):
        return self.decl.returnType

    def emitLoad(self, gen):
        if not self.decl.flags.static:
            thisType = self.this.getType()
            if thisType.builder.IsValueType or thisType.builder.IsPrimitive:
                self.this.emitLoadAddress(gen)
            else:
                self.this.emitLoad(gen)

        assert self.decl is not None, self
        assert self.decl.builder is not None, self.decl

        for arg in self.args:
            arg.emitLoad(gen)

        if self.decl.flags.virtual or self.decl.flags.abstract:
            gen.ilGen.Emit(gen.opCodes.Callvirt, self.decl.builder)
        else:
            gen.ilGen.Emit(gen.opCodes.Call, self.decl.builder)
