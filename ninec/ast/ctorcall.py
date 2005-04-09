
import CLR
from CLR import System

from nine import error

class CtorCall(object):
    def __init__(self, type, args):
        self.position = (0, '<unknown>')
        self.type = type
        self.args = args
        self.ctorInfo = None

    def getType(self):
        return self.type

    def semantic(self, scope):
        #assert len(self.args) == 0, 'Non-default constructors on user classes are not yet implemented. %r' % self.args

        return self

    def emitLoad(self, gen):
        assert self.type.builder is not None, self.type

        ctor = self.type.getCtor(self.args)
        assert ctor is not None, self

        builder = ctor.builder
        assert builder is not None, (self, ctor)

        for arg in self.args:
            arg.emitLoad(gen)

        gen.ilGen.Emit(gen.opCodes.Newobj, builder)
