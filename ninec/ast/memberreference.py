
from ast import vartypes

class MemberReference(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.memberInfo = None

    def semantic(self, scope):
        classType = self.lhs.getType()
        self.memberInfo = classType.builder.GetField(self.rhs.name)
        assert self.memberInfo is not None
        return self


    def getType(self):
        return vartypes.Type.getNineType(self.memberInfo.FieldType)

    def emitCode(self, gen):
        self.lhs.emitCode(gen)
        gen.ilGen.Emit(gen.opCodes.Ldfld, self.memberInfo)
