
import unittest

from nine import error

from tests import util

class SelfTest(unittest.TestCase):
    def testSemantic(self):
        program = util.source('''
            class Test1:
                def Foo():
                    print self
        ''')

        util.semanticProgram(program)

    def testGlobalFuncSelf(self):
        program = util.source('''
            def GlobalFunc():
                print self
        ''')

        self.assertRaises(
            error.SyntaxError,
            lambda: util.semanticProgram(program)
        )

    def testModuleScopeSelf(self):
        program = util.source('print self')

        self.assertRaises(
            error.SyntaxError,
            lambda: util.semanticProgram(program)
        )

    def testFunctionScopeSelf(self):
        program = util.source('''
            def Foo():
                print self
        ''')

        self.assertRaises(
            error.SyntaxError,
            lambda: util.semanticProgram(program)
        )

    def testStaticMethodScopeSelf(self):
        program = util.source('''
            class Test:
                static def Foo():
                    print self
        ''')

        self.assertRaises(
            error.SyntaxError,
            lambda: util.semanticProgram(program)
        )

    def testCodeGen(self):
        program = util.source('''
            class CodeGenTest:
                def Method():
                    print self

            var t = CodeGenTest()
            t.Method()
        ''')

        util.runProgram('self_codegen_test', program)

if __name__ == '__main__':
    unittest.main()
