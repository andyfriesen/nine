
import unittest

from ast.classdecl import ClassDecl

from nine import error
from nine.lexer import lex

from tests import util

class ClassDeclTest(unittest.TestCase):
    def testParse1(self):
        'Return the ClassDecl so that the testSemanticX methods can use it.'
        program = util.source('''
            class NineTest:
                pass
        ''')

        result = util.parseProgram(program)
        assert isinstance(result[0], ClassDecl)
        return result[0]

    def testParse2(self):
        program = util.source('''
            class NineTest:
                def Method():
                    pass
        ''')

        result = util.parseProgram(program)
        assert isinstance(result[0], ClassDecl)
        return result[0]

    def testParse3(self):
        program = util.source('''
            class NineTest:
                var memberVar
        ''')

        result = util.parseProgram(program)
        assert isinstance(result[0], ClassDecl)
        return result[0]

    def testParse4(self):
        program = util.source('''
            class NineTest:
                var memberVar

                pass

                def Method():
                    pass
        ''')

        result = util.parseProgram(program)
        assert isinstance(result[0], ClassDecl)
        return result[0]

    def testSemantic1(self):
        util.semanticProgram(
            util.source('''
                class NineTest:
                    pass
            ''')
        )

    def testSemantic2(self):
        util.semanticProgram(
            util.source('''
                class NineTest:
                    var x
                    def Method():
                        pass
            ''')
        )

    def testSemantic2(self):
        program = util.source('''
            class DuplicateName:
                pass

            class DuplicateName:
                var x
                def Method():
                    pass
        ''')

        self.failUnlessRaises(
            error.NameError,
            lambda: util.semanticProgram(program)
        )

    def testCodeGen(self):
        program = util.source('''
            class NineTest:
                var x as int
                def Method():
                    pass
        ''')

        util.buildProgram('classdecl_codegen_test', program)

    def testAttributes(self):
        program = util.source('''
            class NineTest:
                var x as int
                def Method():
                    self.x = self.x + 1
                    print self.x

            var t = NineTest()
            while t.x < 10:
                t.Method()
        ''')

        util.runProgram('classdecl_attribute_test', program)

    def testStaticMethod(self):
        program = util.source('''
            class NineTest:
                static def Method():
                    x = x + 1
                    print x

            var x = 0
            while x < 10:
                NineTest.Method()
        ''')

        util.runProgram('classdecl_static_method_test', program)

    def testStaticAttribute(self):
        program = util.source('''
            class NineTest:
                static var x as int

                def Method():
                    self.x = self.x + 1
                    print self.x

            var t = NineTest()
            while NineTest.x < 10:
                t.Method()
        ''')

        util.runProgram('classdecl_static_attr_test', program)

    def testOverride(self):
        program = util.source('''
            class Base:
                var x as int

                def NonVirtual():
                    print 'nonvirtual'
                    print self.x
                    self.x += 1

                virtual def Method():
                    print 'Base!'

                def wuzzah():
                    print 'wuzzah!'
                    print self.x

            class Child1(Base):
                override def Method():
                    print 'Child1!'

            class Child2(Base):
                override def Method():
                    print 'Child2!'

            var t = Base()

            t.Method()
            t.NonVirtual()
            t.wuzzah()

            t = Child1()
            t.Method()
            t.NonVirtual()
            t.wuzzah()

            t = Child2()
            t.Method()
            t.NonVirtual()
            t.wuzzah()
        ''')

        util.runProgram('classdecl_override_test', program)

    def testGetMethod(self):
        "testGetMethod: Test ClassDecl.getMethod()"
        from ast import vartypes

        program = util.source('''
            class A_Class:
                virtual def Method():
                    pass

            #class B_Class(A_Class):
            #    override def Method():
            #        pass
        ''')

        result = util.semanticProgram(program).pop()
        assert isinstance(result, ClassDecl)

        assert result.getMethod("Method", (), vartypes.VoidType) is not None

    def testVirtualOverrideKeywords1(self):
        program = util.source('''
            class A_Class:
                override def Bork():
                    pass
        ''')

        self.assertRaises(
            error.OverrideError,
            lambda: util.semanticProgram(program)
        )

    def testVirtualOverrideKeywords2(self):
        program = util.source('''
            class A_Class:
                override def Method():
                    pass
            class B_Class(A_Class):
                override def Method(x as int):
                    pass
            '''
        )

        self.assertRaises(
            error.OverrideError,
            lambda: util.semanticProgram(program)
        )

    def testVirtualOverrideKeywords3(self):
        program = util.source('''
            class A_Class:
                virtual def Method():
                    pass
            class B_Class(A_Class):
                override def Method():
                    pass
        ''')

        util.semanticProgram(program)

    def testSealedMethod(self):
        program = util.source('''
            class A:
                virtual def Method():
                    print 'A'

            class B(A):
                sealed override def Method():
                    print 'B'

            class C(B):
                override def Method():
                    print 'C'
        ''')

        self.assertRaises(
            error.OverrideError,
            lambda: util.semanticProgram(program)
        )

    def testCircularInheritance(self):
        self.fail("Known to fail.  Has to do with the order in which declarations are semantically tested.  Must fix.")
        program = util.source('''
            class A(B):
                pass

            class B(A):
                pass
        ''')

        self.assertRaises(
            error.OverrideError,
            lambda: util.semanticProgram(program)
        )

    def testSealedClass(self):
        program = util.source('''
            sealed class A:
                virtual def Method():
                    print 'Hody2!'

            class B(A):
                pass
        ''')

        self.assertRaises(
            error.OverrideError,
            lambda: util.buildProgram('classdecl_sealedclass_test', program)
        )

    def testAbstractClass(self):
        program = util.source('''
            abstract class A:
                abstract def Foo()

            class B(A):
                override def Foo():
                    print 'B.Foo'

            class C(A):
                override def Foo():
                    print 'C.Foo'

            var a as A
            a = B()
            a.Foo()

            a = C()
            a.Foo()
        ''')

        util.runProgram('classdecl_abstract_class_test', program, ['mscorlib'])

    def testStaticFactory(self):
        # Test a problem that occurred when trying to construct an instance
        # of a class within methods of that class.

        program = util.source('''
            class Test:
                static def MakeTest() as Test:
                    var test = Test()
                    return test

            var t = Test.MakeTest()
        ''')

        util.runProgram('classdecl_static_factory_test', program)

if __name__ == '__main__':
    unittest.main()
