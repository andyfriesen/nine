import ast.external

import unittest

from ast.external import *

from nine.driver import Driver
from ast.namespace import Namespace

from tests import util

if 'set' not in globals():
    from sets import Set as set

class ExternTest(unittest.TestCase):
    def testScanAssembly(self):
        from nine.scope import Scope
        from ast.namespace import Namespace

        scope = Scope(parent=None)
        globalNs = Namespace('')

        driver = Driver()
        driver.addReference('bin/ClassLibrary1')
        driver._scanAssembly(globalNs, 'bin/ClassLibrary1')

        cls = globalNs.symbols['TestClass'].symbols['TestClass']

        assert isinstance(cls, ExternalClass)
        assert cls.external

        self.assertEqual(cls.name, 'TestClass')

    def testReadAttribute(self):
        program = util.source('''
            var o = TestClass.TestClass()
            print o.x
        ''')

        util.runProgram('extern_read_attr_test', program, ['bin/ClassLibrary1'])

    def testWriteAttribute(self):
        program = util.source('''
            var o = TestClass.TestClass()
            o.x = 999
            print o.x
        ''')

        util.runProgram('extern_write_attr_test', program, ['bin/ClassLibrary1'])

    def testReadStaticAttribute(self):
        program = util.source('''
            print TestClass.TestClass.s
        ''')

        util.runProgram('extern_read_static_attr_test', program, ['bin/ClassLibrary1'])

    def testWriteStaticAttribute(self):
        program = util.source('''
            TestClass.TestClass.s = 9
        ''')

        util.runProgram('extern_write_static_attr_test', program, ['bin/ClassLibrary1'])

    def testCallMethod(self):
        program = util.source('''
            var o = TestClass.TestClass()
            o.Method('Hello to C# from Nine!')
        ''')

        util.runProgram('extern_method_test', program, ['bin/ClassLibrary1'])

    def testCallStaticMethod(self):
        program = util.source('''
            TestClass.TestClass.StaticMethod('Calling static method from Nine!')
        ''')

        util.runProgram('extern_static_method_test', program, ['bin/ClassLibrary1'])

    def testResolveOverload(self):
        program = util.source('''
            var o = TestClass.TestClass(2)
            o.Method(9)
            #o.Method('String!')
        ''')

        util.runProgram('extern_overload_test', program, ['mscorlib', 'bin/ClassLibrary1'])

    def testFailResolveOverload(self):
        program = util.source('''
            var o = TestClass.TestClass(2)
            o.Method(o)
        ''')

        self.assertRaises(
            error.TypeError,
            lambda: util.buildProgram('extern_overload_fail_test', program, ['mscorlib', 'bin/ClassLibrary1'])
        )

    def testReadProperty(self):
        program = util.source('''
            var o = TestClass.TestClass(2)
            print o.Property
        ''')

        util.runProgram('extern_read_property_test', program, ['mscorlib', 'bin/ClassLibrary1'])

    def testWriteProperty(self):
        program = util.source('''
            var o = TestClass.TestClass(2)
            o.Property = 'Nine!'
            print o.Property
        ''')

        util.runProgram('extern_write_property_test', program, ['mscorlib', 'bin/ClassLibrary1'])

    def testGetMethod(self):
        driver = Driver()
        ns = Namespace('')
        driver._scanAssembly(ns, 'mscorlib')

        console = ns.symbols['System'].symbols['Console']

        writeLineStr = console.getMethod('WriteLine', (System.String,), System.Void)
        assert writeLineStr is not None

        nonExistent = console.getMethod('WriteLine', (System.String,), System.Single)
        assert nonExistent is None, writeLineStr

        toStr = console.getMethod('ToString', (), System.String)
        assert toStr is not None

    def testGetMethods(self):
        'testGetMethods: ClassDecl.getMethods'
        driver = Driver()
        ns = Namespace('')
        driver._scanAssembly(ns, 'bin/ClassLibrary1')

        class1 = ns.symbols['TestClass'].symbols['TestClass']
        assert isinstance(class1, ExternalClass)

        names = set([func.name for func in class1.getMethods()])
        expected = set(['Method', 'Method', 'StaticMethod', 'StaticMethod'])

        # There will be all kinds of other crud in there.  None of it matters, as long as the right names are where they should be.
        self.failUnless(names > expected, (names, expected))

    def testGetCtor(self):
        from ast.parameter import Parameter

        driver = Driver()
        ns = Namespace('')
        driver._scanAssembly(ns, 'mscorlib')

        string = ns.symbols['System'].symbols['String']
        int32 = ns.symbols['System'].symbols['Int32']
        char = ns.symbols['System'].symbols['Char']

        c1args = (
            Parameter((0,"<>"), 'a', char),
            Parameter((0,"<>"), 'b', int32)
        )
        c2args = (Parameter((0,"<>"), 'b', int32),)

        c1 = string.getCtor(c1args)
        c2 = string.getCtor(c2args)

        assert c1 is not None
        assert c2 is None

    def testGetNestedType(self):
        program = util.source('''
            var o as TestClass.TestClass.NestedClass
        ''')

        util.semanticProgram(program, ['ClassLibrary1'])

    def testOverride(self):
        program = util.source('''
            class MyClass(System.Object):
                override def ToString() as string:
                    return "Hello, overriding Object.ToString here!"

            var cls = MyClass()
            print cls
        ''')

        util.runProgram('external_override_test', program, ['mscorlib'])

    def testOverride2(self):
        program = util.source('''
            class MyClass(System.Object):
                virtual def ToString() as string:
                    return "Shouldn't work!"
        ''')

        self.assertRaises(
            error.OverrideError,
            lambda: util.semanticProgram(program, ['mscorlib'])
        )

    def testOverride3(self):
        program = util.source('''
            class MyClass(System.Object):
                override def ToString(x as int) as string:
                    return "Also shouldn't work"
        ''')

        self.assertRaises(
            error.OverrideError,
            lambda: util.semanticProgram(program, ['mscorlib'])
        )

    def testOverrideExternalClassMethod(self):
        program = util.source('''
            class MyClass(TestClass.PublicClass):
                override def Foo(x as int):
                    print 'MyClass.Foo'
                    print x

            var o as TestClass.PublicClass
            o = MyClass()
            o.Foo(9)
        ''')

        util.runProgram('implement_override_external_class_method_test', program, ['bin/ClassLibrary1'])

    def testImplementExternalInterface(self):
        program = util.source('''
            class MyClass(TestClass.ExternalInterface):
                def Foo():
                    print 'Foo!!'

                def Bar():
                    print 'Bar!!111juan'

            var o as TestClass.ExternalInterface
            o = MyClass()
            o.Foo()
        ''')

        util.runProgram('implement_external_interface_test', program, ['bin/ClassLibrary1'])

    def testIncompleteExternalInterface(self):
        program = util.source('''
            class MyClass(TestClass.ExternalInterface):
                def Foo():
                    print 'Foo!'

            var o as TestClass.ExternalInterface
            o = MyClass()
            o.Foo()
        ''')

        self.assertRaises(
            error.OverrideError,
            lambda: util.buildProgram('incomplete_external_interface_test', program, ['bin/ClassLibrary1'])
        )

    def testCallValueTypeMember(self):
        program = util.source('''
            var pi = 3.1415926535897931
            print 'Pi:'
            print pi.ToString()
        ''')

        util.runProgram('extern_call_value_type_member_test', program)

if __name__ == '__main__':
    unittest.main()
