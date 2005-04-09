
import unittest

from tests import util

class ForTest(unittest.TestCase):
    def testParse(self):
        util.parseProgram(util.source('''
            for my_iter in collection:
                pass
        '''))

    def testParseWithType(self):
        util.parseProgram(util.source('''
            for my_iter as T in collection:
                pass
        '''))

    def testRun(self):
        util.runProgram('for_test', util.source('''
            var a = array(string, 4)
            a[0] = 'N'
            a[1] = 'I'
            a[2] = 'N'
            a[3] = 'E'

            for c in a:
                print c
        '''))

    def testIntArray(self):
        util.runProgram('for_int_array_test', util.source('''
            var a = array(int, 4)
            a[0] = 1
            a[1] = 1
            a[2] = 2
            a[3] = 3

            for c in a:
                print c
        '''))

    def testUserClassArray(self):
        util.runProgram('for_user_class_array_test', util.source('''
            class Test:
                static var instances as array(Test)
                static var numInstances as int

                def ctor():
                    Test.numInstances += 1

                def printAll():
                    for i in Test.instances:
                        print i
        '''))

    def testInsanity(self):
        util.runProgram('for_insanity_test', util.source('''
            class Vertex:
                def Draw():
                    pass

            class Quad:
                var verts as array(Vertex)

                def Draw():
                    for v in self.verts:
                        v.Draw()
        '''))

    def testNestedLoops(self):
        util.runProgram('for_nest_test', util.source('''
            var x = array(int, 5)

            for a in x:
                for b in x:
                    print a + b
        '''))

if __name__ == '__main__':
    unittest.main()
