from tests import util
import unittest

class DelegateTest(unittest.TestCase):
    def testCreateType(self):
        program = util.source('''
            delegate MyDelegate(a as int) as string
            '''
        )

        util.runProgram('delegate_type_test', program, [])

    def testAssignDelegate(self):
        program = util.source('''
            def output(a as int):
                print a

            delegate MyDelegate(a as int)

            var b = MyDelegate(output)'''
        )

        util.runProgram('delegate_assign_test', program, [])

    def testCallDelegate(self):
        program = util.source('''
            def output(a as string) as string:
                return a

            delegate MyDelegate(zz as string) as string

            var b = MyDelegate(output)

            print b("Calling output through MyDelegate!")'''
        )

        util.runProgram('delegate_call_test', program, [])

    def testAssignDelegateExternal(self):
        program = util.source('''
            delegate ExternDelegate(arg as System.Double) as System.Double

            var b = ExternDelegate(System.Math.Cos)
            '''
        )

        util.runProgram('delegate_external_assign_test', program, ['mscorlib'])

    def testAssignDelegateExternalOverloaded(self):
        program = util.source('''
            delegate ExternDelegate(a as int) as string

            var b = ExternDelegate(System.Convert.ToString)

            print b(9)'''
        )

        util.runProgram('delegate_external_overloaded_assign_test', program, ['mscorlib'])

    def testDelegateInstanceMethod(self):
        program = util.source('''
            class Cls:
                def out(a as string):
                    print a

            var b = Cls()
            b.out("You should see 9:")

            delegate InstanceOutput(str as string)

            var c = InstanceOutput(b.out)
            c("9")
            '''
        )

        util.runProgram('delegate_instance_method', program, [])

    def testDelegateInstanceMethod(self):
        program = util.source('''
            var b = System.Object()

            delegate InstanceOutput() as System.Type

            var c = InstanceOutput(b.GetType())

            print "You should see 'System.Object':"
            print c()
            '''
        )

        util.runProgram('delegate_external_instance_method', program, ['mscorlib'])

if __name__=='__main__':
    unittest.main()
