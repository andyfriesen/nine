
import CLR
from CLR import System

from nine import error

class DelegateCtorCall(object):
    def __init__(self, type, args):
        self.position = (0, '<unknown>')
        self.type = type
        self.args = args

    def getType(self):
        return self.type

    def semantic(self, scope):
        return self

    def _getLoadArgs(self, arg):
        from ast.functiondecl import FunctionDecl
        from ast import classdecl
        from ast import external

        mi = None
        this = None
        staticFlag = False

        if isinstance(arg, FunctionDecl):
            staticFlag = True
            this = None
            mi = arg.builder
        
        elif isinstance(arg, external.ExternalMethodCall):
            staticFlag = arg.methodInfo.IsStatic
            this = arg.this
            mi = arg.methodInfo
        
        elif isinstance(arg, external.UnresolvedMethod):
            # use .apply() method with argument types to work out the correct overload
            mc = arg.apply(self.type.params)
            assert mc is not None, self

            staticFlag = mc.methodInfo.IsStatic
            this = mc.this

            mi = mc.methodInfo

        elif isinstance(arg, classdecl._MethodReference):
            # use .apply() method with argument types to work out the correct overload
            mc = arg.apply(self.type.params)
            assert mc is not None, self

            staticFlag = mc.decl.flags.static
            this = mc.this
            mi = mc.decl.builder

        assert staticFlag or this is not None, 'Internal error: have no subject for nonstatic method %r' % arg.name

        return mi, this, staticFlag

    def emitLoad(self, gen):
        from ast.vartypes import VoidType
        from nine import util
        assert self.type.builder is not None, self.type

        ctor = self.type.getCtor(self.args)
        if ctor is None:
            # FIXME: these sorts of errors really should be raised during semantic phase, not codegen!!
            raise error.SyntaxError(self.type.position, "Method argument signature does not match Delegate signature")

        builder = ctor.builder
        assert builder is not None, self

        #delegates should only have one arg
        assert len(self.args) == 1, (self, self.args)

        arg = self.args[0]
        assert arg is not None, "%s %r" % (self, arg)

        mi, this, staticFlag = self._getLoadArgs(arg)

        if staticFlag:
            # All delegates must push a subject argument.
            # Push 'null' for static methods.
            gen.ilGen.Emit(gen.opCodes.Ldnull)

        elif this is not None:
            this.emitLoad(gen)

        else:
            # assume it is in an instance of self?
            gen.ilGen.Emit(gen.opCodes.Ldarg_0)

        gen.ilGen.Emit(gen.opCodes.Ldftn, mi)
        gen.ilGen.Emit(gen.opCodes.Newobj, builder)
