
import unittest

from tests import util

class ExpressionStatementTest(unittest.TestCase):
    def testCodeGen(self):
        program = util.source('''
            5+2
        ''')

        util.buildProgram('expression_statement_test', program)

if __name__ == '__main__':
    unittest.main()
