
import os.path

import CLR
from CLR import System
from CLR.System import Threading
from CLR.System import Reflection
from CLR.System.Reflection import Emit

from ast import vartypes

class CodeGenerator(object):
    # Get some references to enums and things that will be frequently useful for code generation.
    # This alleviates the need to pepper .NET imports all over the compiler.
    opCodes = Emit.OpCodes                              # FIXME: should use PascalCase (OpCodes, not opCodes)
    TypeAttributes = Reflection.TypeAttributes
    MethodAttributes = Reflection.MethodAttributes
    MethodImplAttributes = Reflection.MethodImplAttributes
    FieldAttributes = Reflection.FieldAttributes
    CallingConventions = Reflection.CallingConventions

    def __init__(self, gen=None):
        if gen is not None:
            self.programName = gen.programName
            self.asmBuilder = gen.asmBuilder
            self.module = gen.module
            self.typeBuilder = gen.typeBuilder
            self.methodBuilder = gen.methodBuilder
            self.ilGen = gen.ilGen

            self.breakLabel = gen.breakLabel
            self.continueLabel = gen.continueLabel

        else:
            self.breakLabel = None
            self.continueLabel = None

    def createAssembly(self, exeName):
        path, name = os.path.split(exeName)
        name, ext = os.path.splitext(name)

        if not ext:
            ext = '.exe'

        self.programName = name

        domain = Threading.Thread.GetDomain()
        asmName = Reflection.AssemblyName()
        asmName.Name = name

        self.asmBuilder = domain.DefineDynamicAssembly(
            asmName,
            Emit.AssemblyBuilderAccess.Save,
            path or None
        )

        self.module = self.asmBuilder.DefineDynamicModule(
            name,
            name + ext
        )

        # TEMP: create the Main Class thing.
        self.typeBuilder = self.module.DefineType(
            'NineMainClass',
            Reflection.TypeAttributes.Public
        )

        stringArrayType = System.Array.CreateInstance(System.String, 0).GetType()

        mainArgs = System.Array.CreateInstance(System.Type, 1)
        mainArgs[0] = stringArrayType

        # "public static void main(string[] args)"
        self.mainMethod = self.typeBuilder.DefineMethod(
            'Main',
            Reflection.MethodAttributes.Public |
            Reflection.MethodAttributes.Static,
            System.Void,
            mainArgs
        )

        self.methodBuilder = self.mainMethod

        self.ilGen = self.methodBuilder.GetILGenerator()

    def defineGlobal(self, name, type):
        assert type.builder is not None, 'Internal error: type %r has no builder' % type

        ilType = type.builder

        builder = self.typeBuilder.DefineField(name, ilType, Reflection.FieldAttributes.Public | Reflection.FieldAttributes.Static)

        return builder

    def defineLocal(self, type):
        assert type.builder is not None, 'Internal error: type %r has no builder' % type

        ilType = type.builder

        builder = self.ilGen.DeclareLocal(ilType)
        return builder

    def defineVariable(self, name, type):
        return self.defineGlobal(name, type)

    def closeAssembly(self):
        self.typeBuilder.CreateType()
        self.asmBuilder.SetEntryPoint(self.mainMethod)
        self.asmBuilder.Save(self.programName + '.exe')

    def emitCode(self, program):
        '''Code generation happens in three stages:
            First, type builders are created.
            Method builders are created in the second stage.
            Actual function bodies are not processed until the third stage.

        This way, there is no possibility of things getting tied up into knots
        because of circular dependancies.  Things like mutually recursive
        functions will be able to access each others' builders without issue.
        '''
        for statement in program:
            if hasattr(statement, 'emitType'):
                statement.emitType(self)

        for statement in program:
            if hasattr(statement, 'emitDeclaration'):
                statement.emitDeclaration(self)

        for statement in program:
            statement.emitCode(self)

    def createProgram(self, name, program):
        self.createAssembly(name)

        self.emitCode(program)

        self.ilGen.Emit(Emit.OpCodes.Ret)

        self.closeAssembly()
