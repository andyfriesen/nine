
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

    def testUserClassArray(self):
        util.runProgram('for_user_class_array_test', util.source('''
            class Test:
                static var instances as array(Test)

                def ctor():
                    Test.instances += 1

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
                        (v as Vertex).Draw()
        '''))

if __name__ == '__main__':
    unittest.main()
