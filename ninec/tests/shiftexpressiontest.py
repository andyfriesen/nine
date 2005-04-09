
import unittest

from tests import util

class ShiftExpressionTest(unittest.TestCase):
    def testParse(self):
        program = '''var x = 3<<2'''
        util.parseProgram(program)

    def testSemantic(self):
        program = '''var x = 3<<2'''
        util.semanticProgram(program)

    def testBadSemantic(self):
        program = '''var x = 3.3<<2'''
        try:
            util.semanticProgram(program)
        except:
            assert True

    def testBad2Semantic(self):
        program = '''var x = 3<<2.2'''
        try:
            util.semanticProgram(program)
        except:
            assert True

    def testCodeEmit(self):
        program = util.source('''
            var x = 3<<2
            var y = 1<<8
            print 'first 12 then 256'
            print x
            print y
        ''')

        util.runProgram('shiftTest', program)
