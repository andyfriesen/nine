import unittest
from tests import util


class MemberReferenceTest(unittest.TestCase):
    def testSemantic(self):
        program = util.source('''
            var x = TestClass.TestClass()
            var y = x.x
            ''')
        result = util.semanticProgram(program, ['bin/ClassLibrary1'])


    def testCodeGeneration(self):
        program = util.source('''
            var x = TestClass.TestClass()
            var y = x.x
            print y
            y = 2
            print y
            ''')
        result = util.runProgram('memberreferencetest', program, ['bin/ClassLibrary1'])




if __name__ == '__main__':
    unittest.main()
