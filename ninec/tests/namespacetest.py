
import unittest

from tests import util

class NamespaceTest(unittest.TestCase):
    def testParameter(self):
        program = util.source('''
            def foo(c as System.Type):
                pass
        ''')

        util.buildProgram('namespace_parameter_test', program, ['mscorlib'])

    def testReturnType(self):
        program = util.source('''
            def foo() as System.Object:
                pass
        ''')

        util.buildProgram('namespace_return_test', program, ['mscorlib'])

    def testValue(self):
        program = util.source('''
            var t as System.Reflection.Assembly
            print t
        ''')

        util.buildProgram('namespace_variable_test', program, ['mscorlib'])

if __name__ == '__main__':
    unittest.main()
