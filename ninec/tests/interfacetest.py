
import unittest

from nine import error

from tests import util

class InterfaceTest(unittest.TestCase):
    def testParseEmptIface(self):
        program = util.source('''
            interface Foo:
                pass
        ''')

        util.parseProgram(program)

    def testParse(self):
        program = util.source('''
            interface Foo:
                def A(a as int) as void
                def B() as int
        ''')

        util.parseProgram(program)

    def testMethodDef(self):
        program = util.source('''
            interface Foo:
                def B() as int:
                    pass
        ''')

        self.assertRaises(
            error.SyntaxError,
            lambda: util.parseProgram(program)
        )

    def testEmptyInterface(self):
        program = util.source('''
            interface Foo:
                pass
        ''')

        util.buildProgram('interface_empty_test', program)

    def testBuildInterface(self):
        program = util.source('''
            interface TestIface:
                def foo() as int
                def bar(a as int)
                def baz(b as string) as string
        ''')

        util.buildProgram('interface_build_test', program)

    def testImplementInterface(self):
        program = util.source('''
            interface Firable:
                def fire() as void

            class Employee(Firable):
                def fire() as void:
                    print 'Firing employee!'

            class Missle(Firable):
                def fire() as void:
                    print 'Initiating thermonuclear war with China for fun and profit.'
        ''')

        util.buildProgram('interface_implement_test', program)

    def testImplementInterface2(self):
        program = util.source('''
            interface Firable:
                def fire() as void

            class Employee(Firable):
                def fire() as void:
                    print 'Firing employee!'

            class Missle(Firable):
                def fire() as void:
                    print 'Initiating thermonuclear war with China for fun and profit.'

            var f as Firable

            f = Employee()
            f.fire()

            f = Missle()
            f.fire()
        ''')

        util.runProgram('interface_implement2_test', program)

    def testIncompleteInterface(self):
        program = util.source('''
            interface Duck:
                def quack() as void

            class Foo(Duck):
                pass
        ''')

        self.assertRaises(
            error.OverrideError,
            lambda: util.buildProgram('interface_incomplete_test', program)
        )

if __name__ == '__main__':
    unittest.main()
