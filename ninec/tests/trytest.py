
import unittest
from ast.trystatement import TryStatement
from tests import util
from nine import error

class TryTest(unittest.TestCase):
    def testParse(self):
        program = util.source('''
            try:
                pass
            except a:
                pass
            finally:
                pass
        ''')

        ast = util.parseProgram(program)
        self.assertTrue(isinstance(ast[0], TryStatement))

        stmt = ast[0]
        self.assertEqual(1, len(stmt.exceptBlocks))
        self.assertNotEqual(None, stmt.finallyBlock)

    def testParseTryFinally(self):
        program = util.source('''
            try:
                pass
            finally:
                pass
        ''')

        ast = util.parseProgram(program)
        self.assertTrue(isinstance(ast[0], TryStatement))

        stmt = ast[0]
        self.assertEqual([], stmt.exceptBlocks)
        self.assertNotEqual(None, stmt.finallyBlock)

    def testParseNoExceptOrFinally(self):
        program = util.source('''
            try:
                pass
        ''')

        self.assertRaises(error.SyntaxError, lambda: util.parseProgram(program))

    def testSemantic(self):
        program = util.source('''
            try:
                pass
            except:
                pass
            finally:
                pass'''
        )

        st = util.semanticProgram(program, [])
        self.assertNotEqual(None, st)

    def testSemanticTryFinallyExcept(self):
        program = util.source('''
            try:
                pass
            finally:
                pass
            except:
                pass'''
        )

        self.assertRaises(Exception, lambda: util.semanticProgram(program, []))

    #TODO: add test to check semantics of a except that runs on a specific Exception

    def testCatchAll(self):
        program = util.source('''
            var nine = 9
            var nullObj as System.Object

            try:
                print 'Nine = ' + nine.ToString()
                print 'This line should not be visible.  ' + nullObj.ToString()
            except:
                print 'Hurray, caught the expression!'
            finally:
                print 'Finally!'
        ''')

        util.runProgram('try_catch_all_test', program, ['mscorlib'])

    def testFilter(self):
        program = util.source('''
            var nine = 9
            var nullObj as System.Object

            try:
                print nullObj.ToString()
                print 'No exception thrown. @_@'
            except System.NullReferenceException:
                print 'Caught NullReferenceException!'
            except:
                print "You shouldn't see this!"
        ''')

        util.runProgram('try_filter_test', program, ['mscorlib'])

    def testFinally(self):
        program = util.source('''
            var nine = 9
            var nullObj as System.Object

            try:

                try:
                    print nine
                    print "This should freak out" + nullObj.ToString()
                finally:
                    print 'We should see this!'

            except System.NullReferenceException:
                pass
        ''')

        util.runProgram('try_finally_test', program, ['mscorlib'])

    def testExceptInstance(self):
        program = util.source('''
            var nullObj as System.Object

            try:
                print 'Fishing for errors...'
                print nullObj.ToString()
            except e as System.NullReferenceException:
                print "Hey look we caught something:"
                print "   " + e.ToString()
            '''
        )

        util.runProgram('try_exception_instance_test', program, ['mscorlib'])

    def testUserExceptType(self):
        program = util.source('''
            class UserException(System.Exception):
                pass

            try:
                raise UserException()
            except UserException:
                print "User exceptions work!"'''
        )

        util.runProgram('try_user_except_test', program, ['mscorlib'])

if __name__=='__main__':
    unittest.main()
