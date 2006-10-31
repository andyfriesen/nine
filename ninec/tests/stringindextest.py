import unittest
from tests import util

class StringIndexTest(unittest.TestCase):
    def testCharEmitLoad(self):
        p=util.source('''
            var a = "x"
            var b = 'y'
            
            print "see x then y:"
            print a[0]
            print b[0]
        ''')
        util.runProgram('TestCharEmitLoad',p)
    
    def testSetChar(self):
        #TODO: this requires some fancy work, because System.String has no 'set' method
        assert False, "I would like to get this to work"
        p=util.source('''
            var a = "x"
            var b = 'y'
            
            print "see x then y:"
            print a[0]
            a[0]=b[0]
            print a[0]
        ''')
        util.runProgram('TestCharEmitLoad',p)
        
    def testAssignChar(self):
        p=util.source('''
            var a = "niNe"
            var b as char= a[2]
            
            print "see N:"
            print b
        ''')
        util.runProgram('TestCharEmitLoad',p)
    
if __name__=="__main__":
    unittest.main()