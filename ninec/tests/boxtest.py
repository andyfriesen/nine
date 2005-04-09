import unittest

from nine.lexer import lex
from nine.tokenlist import TokenList

from tests import util


class BoxTest(unittest.TestCase):

    def testAssign(self):
        program = util.source('''
            var oob as System.Object
            var x = 1
            print x
            oob = 1
            print oob
        ''')

        util.runProgram('box_assign_test', program, ['mscorlib'])
    
    def testCast(self):
        program = util.source('''

            var a = 1
            var o as System.Object
            print 'Should see "System.Object":'
            print o
            print 'Should see "1":'
            o = a as System.Object
            print o
            o = 3 as System.Object
            print 'Should see "3":'
            print o
        ''')

        util.runProgram('box_cast_test', program, ['mscorlib'])
        
    def testUnCast(self):
        program = util.source('''

            var a = 1
            var o as System.Object
            
            print 'Should see "5":'
            o = 5
            a = o as System.Int32
            print a
            
            print 'Should see "8":'
            print 3 + o as System.Int32
            
            print 'Should see "5.5":'
            o = 5.5
            print o as System.Single
        ''')

        util.runProgram('unbox_cast_test', program, ['mscorlib'])

if __name__ == '__main__':
    unittest.main()