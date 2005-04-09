
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

if __name__ == '__main__':
    unittest.main()
