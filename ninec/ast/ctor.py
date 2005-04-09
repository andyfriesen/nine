
from ast import functiondecl

from nine import error

class Ctor(functiondecl.FunctionDecl):
    def __init__(self, position, params, body, flags):
        from ast.blockstatement import BlockStatement

        super(Ctor, self).__init__('.ctor', position, None, params, body, flags)
        self.position = position
        self.params = params
        self.body = body or BlockStatement()
        self.flags = flags

        self.klass = None # set during semantic testing
        self.builder = None # set by emitDeclaration

    def semantic(self, scope):
        if scope.klass is None:
            raise error.SyntaxError(self.position, 'Constructors must be declared within a class')

        f = self.flags
        if f.virtual or f.override or f.abstract or f.sealed:
            raise error.SyntaxError(self.position, 'Modifier combination makes no sense on constructors')

        # TODO: see if the class already has more than one constructor with these parameter types

        params = []
        for param in self.params:
            params.append(param.semantic(scope))

        self.params = params

        self.klass = scope.klass

        return self

    def emitDeclaration(self, gen):
        if self.builder is not None: return

        from CLR import System

        flags = gen.MethodAttributes.Public

        if self.flags.static:
            flags |= gen.MethodAttributes.Static

        params = System.Array.CreateInstance(System.Type, len(self.params))
        for index, param in enumerate(self.params):
            params[index] = param.type.builder

        self.builder = self.klass.builder.DefineConstructor(flags, gen.CallingConventions.Standard, params)

    def emitCode(self, gen):
        from CLR import System
        from nine import util
        from nine.codegenerator import CodeGenerator

        subGen = CodeGenerator(gen)
        subGen.ilGen = self.builder.GetILGenerator()
        subGen.methodBuilder = self.builder

        subGen.ilGen.Emit(gen.opCodes.Ldarg_0)

        #FIXME: remove when super() is implemented
        #auto-call super ctor
        base = self.klass.bases[0]
        assert base is not None, "ALL Classes have a base!"
        baseCtor = base.getCtor([])
        subGen.ilGen.Emit(gen.opCodes.Call, baseCtor.builder)

        self.body.emitCode(subGen)
        subGen.ilGen.Emit(subGen.opCodes.Ret)

class DefaultCtor(Ctor):
    def __init__(self):
        from ast.memberflags import MemberFlags
        from ast.blockstatement import BlockStatement

        super(DefaultCtor, self).__init__((0, '<implicit>'), (), BlockStatement(), MemberFlags())

    def emitDeclaration(self, gen):
        from CLR import System

        assert self.klass is not None, self
        assert self.klass.builder is not None, (self, self.klass)

        self.builder = self.klass.builder.DefineConstructor(
            gen.MethodAttributes.Public,
            gen.CallingConventions.Standard,
            System.Type.EmptyTypes
        )

        assert self.builder is not None

    def emitCode(self, gen):
        ilGen = self.builder.GetILGenerator()

        base = self.klass.bases[0]
        assert base is not None

        baseCtor = base.getCtor([])

        assert baseCtor is not None, (self.klass, base)
        assert baseCtor.builder is not None, baseCtor

        ilGen.Emit(gen.opCodes.Ldarg_0)
        ilGen.Emit(gen.opCodes.Call, baseCtor.builder)
        ilGen.Emit(gen.opCodes.Ret)
