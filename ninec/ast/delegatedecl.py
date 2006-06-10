from ast.blockstatement import BlockStatement
from ast import classdecl

from ast.ctor import Ctor
from ast.functiondecl import FunctionDecl
from ast.memberflags import MemberFlags
from ast.parameter import Parameter

from ast import vartypes

from CLR import System

from nine import token, util, error
from nine.scope import Scope

class _DelegateCtor(Ctor):
    def __init__(self, position):
        super(_DelegateCtor, self).__init__(
            position,
            params=[
                    Parameter(position, 'obj', util.getNineType(System.Object)),
                    Parameter(position, 'ftn', util.getNineType(System.IntPtr))
                ],
            body=BlockStatement(),
            flags=MemberFlags()
        )

    def emitDeclaration(self, gen):
        if self.builder is not None: return

        from CLR import System

        flags = gen.MethodAttributes.Public | gen.MethodAttributes.HideBySig | gen.MethodAttributes.RTSpecialName

        params = System.Array.CreateInstance(System.Type, len(self.params))
        for index, param in enumerate(self.params):
            params[index] = param.type.builder

        self.builder = self.klass.builder.DefineConstructor(flags, gen.CallingConventions.Standard, params)

        self.builder.SetImplementationFlags(gen.MethodImplAttributes.Runtime|gen.MethodImplAttributes.Managed)

    def emitLoad(self, gen):
        pass

    def emitCode(self, gen):
        pass

class _InvokeMethod(FunctionDecl):
    def __init__(self, position, params, returnType):
        super(_InvokeMethod, self).__init__(
            'Invoke',
            position,
            returnType,
            params,
            body=None,
            flags=MemberFlags(
                abstract = True         # HACK: Semantic analyzer needs to know why body is None
            )
        )

    def emitDeclaration(self, gen):
        if self.builder is not None: return

        from CLR import System

        params = System.Array.CreateInstance(System.Type, len(self.params))

        for index, param in enumerate(self.params):
            type = param.type
            assert type is not None, 'Cannot deduce type of parameter %s' % param
            assert type.builder is not None, (param, type)
            params[index] = type.builder

        flags = gen.MethodAttributes.Public | gen.MethodAttributes.HideBySig | gen.MethodAttributes.NewSlot | gen.MethodAttributes.Virtual

        self.builder = gen.typeBuilder.DefineMethod(
            self.name,
            flags,
            self.returnType.builder,
            params
        )

        self.builder.SetImplementationFlags(gen.MethodImplAttributes.Runtime|gen.MethodImplAttributes.Managed)

    def emitLoad(self, gen):
        # Nothing!
        pass

    def emitCode(self, gen):
        pass

class DelegateDecl(classdecl.ClassDecl):
    def __init__(self, position, name, params, returnType):
        flags = MemberFlags(sealed = True, public = True)

        self.params = params
        self.returnType = returnType

        bases = [util.getNineType(System.MulticastDelegate)]

        body = classdecl.ClassBody([
            _DelegateCtor(position),
            _InvokeMethod(position, params, returnType)
        ]) # create func Invoke

        super(DelegateDecl, self).__init__(position, name, bases, body, flags)

    def parse(tokens):
        oldPos = tokens.getPosition()

        position = tokens.peek().position

        if tokens.peek() != 'delegate':
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

        tokens.expect(token.END_OF_STATEMENT)

        return DelegateDecl(position, name.value, params, returnType)
    parse = staticmethod(parse)

    def resolveNames(self, scope):
        pass

    def semantic(self, scope):
        # semantic test returnType and params

        self = super(DelegateDecl, self).semantic(scope)

        self.returnType = self.returnType.semantic(scope)

        params = []
        for p in self.params:
            params.append(p.semantic(scope))
        self.params = params

        return self

    def getCtor(self, params):
        if len(params) != 1:
            raise error.SyntaxError(self.position, "Delegate Types only take one argument, a method")

        param = params[0]

        from ast import external
        from ast import classdecl
        from ast.ctor import Ctor

        for decl in self.body.decls:
            if not isinstance(decl, Ctor):
                continue

            elif isinstance(param, FunctionDecl):
                ctorParams = [p.getType() for p in self.params]
                callingParams = [p.getType() for p in param.params]

                if ctorParams == callingParams and self.returnType == param.returnType:
                    return decl

            elif isinstance(param , external.ExternalMethodCall):
                ctorParams = [p.getType() for p in self.params]
                callingParams = [p.getType() for p in param.args]

                if ctorParams == callingParams:
                    return decl

            elif isinstance(param, (
                    external.UnresolvedMethod,
                    classdecl._MethodReference
                )
            ):
                mc = param.apply(self.params)
                if mc is not None:
                    return decl

        else:
            return None

    def apply(self, args):
        from ast.delegatectorcall import DelegateCtorCall

        return DelegateCtorCall(self, args)
