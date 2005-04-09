
import CLR
from CLR import System

from nine import error

class DelegateCall(object):
    def __init__(self, variable, args):
        self.position = variable.position
        self.variable = variable
        self.type = variable.getType()
        self.args = args

    def getType(self):
        return self.type

    def semantic(self, scope):
        return self

    def emitLoad(self, gen):
        assert self.type.builder is not None, self.type
        
        self.variable.emitLoad(gen)
        
        mi = self.type.getMethod("Invoke", self.args, self.type.returnType)
        assert mi is not None, self

        for arg in self.args:
            arg.emitLoad(gen)

        gen.ilGen.Emit(gen.opCodes.Callvirt, mi.builder)
