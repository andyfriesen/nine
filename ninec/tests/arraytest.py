
import unittest

from nine import error

from tests import util

class ArrayTest(unittest.TestCase):
    def testParse(self):
        program = '''var a as array(int)'''

        util.parseProgram(program)

    def testParse2(self):
        program = '''a[2] = 3'''

        util.parseProgram(program)

    def testSemantic(self):
        program = '''var a as array(int, 2)'''

        util.semanticProgram(program, [])

    def testSemantic2(self):
        program = '''var a as array(testy)'''

        self.assertRaises(
            error.NameError,
            lambda: util.semanticProgram(program, [])
        )

    def testCompileString(self):
        program = util.source('''
            var len = 5
            var a as array(int) = array(int, len)

            var i = 0
            while i < a.Length:
                a[i] = i
                i = i + 1

            i = 0
            while i < a.Length:
                print a[i]
                i += 1

            var b = array(float, 1)
            b[0] = 9.9
            print b[0]
        ''')

        util.runProgram('array_test', program, [])

    def testMultiDimArray(self):
        program = util.source('''
            var c = array(float, 1, 2)
            c[0,0] = 3.75
            c[0,1] = 5.25

            print c[0,0]+c[0,1]

            #var d as array(boolean, 3)
        ''')

        util.runProgram('array_multidim_test', program, [])

    def testUserClassArray(self):
        program = util.source('''
            class Thing:
                var name as string

                override def ToString() as string:
                    return string.Concat('Thingie has a name: ', self.name)

            var things = array(Thing, 1)
            things[0] = Thing()
            things[0].name = 'bork'

            var i = 0
            while i < things.Length:
                print things[i]
                i += 1
        ''')

        util.runProgram('array_userclass_test', program)

    def testIndexValueTypeMethod(self):
        program = util.source('''
            var things = array(int, 1)

            print things[0].ToString()
        ''')

        util.runProgram('array_index_value_type_method_test', program)

if __name__ == '__main__':
   unittest.main()
