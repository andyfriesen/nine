
import unittest

from nine import error

from tests import util

class CastTest(unittest.TestCase):
    def testParse(self):
        program = util.source('''
            class Test:
                pass

            var o as System.Object
            var t = Test()
            o = t as System.Object
        ''')

        util.parseProgram(program)

    def testSemantic(self):
        program = util.source('''
            class Test:
                pass

            var o as System.Object
            var t = Test()
            o = t as System.Object
        ''')

        util.semanticProgram(program, ['mscorlib'])

    def testBadCast(self):
        program = util.source('''
            class A:
                pass

            class B:
                pass

            var a as A
            var b = B()
            a = b as A
        ''')

        self.assertRaises(
            error.TypeError,
            lambda: util.semanticProgram(program)
        )

    def testEmitCode(self):
        program = util.source('''
            class A:
                pass

            var a = A()
            var o as System.Object
            o = a as System.Object
            print 'Should see "A":'
            print o
        ''')

        util.runProgram('cast_codegen_test', program, ['mscorlib'])

    def testPrimitiveCast(self):
        program = util.source('''
            var a as System.Single
            var b as System.Double
            var c  = 6
            a = c as System.Single
            b = c as System.Double
            c = a as System.Int32
            
            print 'should see three sixes'
            print a
            print b
            print c
        ''')

        util.runProgram('cast_primitives_test', program, ['mscorlib'])


if __name__ == '__main__':
    unittest.main()
