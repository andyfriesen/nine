
import unittest

from nine import lexer
from nine import error

from ast.attribute import Attribute
from ast.identifier import Identifier

from tests import util

class AttributeTest(unittest.TestCase):
    def testRenameIdentifier(self):
        from nine.lexer import lex
        from ast.qualifiedname import QualifiedName

        name = QualifiedName.parse(lex('Foo.Bar.Baz'))

        newName = Attribute.renameIdentifier(name)

        self.assertEqual(newName.lhs, name.lhs)
        self.assertEqual(newName.lhs.rhs.name, name.lhs.rhs.name)
        self.assertEqual(newName.rhs.name, 'BazAttribute')

    def testParseAttributeNoParameters(self):
        source = '[Thingie]'
        tok = lexer.lex(source)

        result = Attribute.parse(tok)

        self.assertTrue(isinstance(result, Attribute))
        self.assertTrue(isinstance(result.className, Identifier))
        self.assertEqual(result.className.name, 'Thingie')
        self.assertEqual(result.params, [])

    def testParseClassWithAttributeNoParameters(self):
        from ast.classdecl import ClassDecl

        program = util.source('''
            class X:
                [Thingie]
                pass
        ''')

        ast = util.parseProgram(program)

        x = ast[0]
        self.assertTrue(isinstance(x, ClassDecl))
        self.assertEqual(len(x.body.attributes), 1)
        self.assertTrue(isinstance(x.body.attributes[0], Attribute))

    def testSemanticClassWithAttribute(self):
        from ast.classdecl import ClassDecl

        program = util.source('''
            class X:
                [TestClass.Thingie]
                pass
        ''')

        result = util.semanticProgram(program, ['bin/ClassLibrary1'])

        x = result[0]
        self.assertTrue(isinstance(x, ClassDecl))

        self.assertEqual(1, len(x.attributes))

        attr = x.attributes[0]

        self.assertEqual('ThingieAttribute', attr.className.name)

    def testClassNoAttributeExists(self):
        program = util.source('''
            class X:
                [ThisNameIsNotDefined]
        ''')

        self.assertRaises(
            error.NameError,
            lambda: util.semanticProgram(program)
        )

    def testAttributeCodeGeneration(self):
        program = util.source('''
            class X:
                [TestClass.Thingie]
                pass
        ''')

        util.buildProgram('attribute_code_generation_test', program, ['bin/ClassLibrary1'])

        # Load the resulting executable and check that the attribute is there
        import CLR
        from CLR.System import String
        from CLR.System.Reflection import Assembly

        program = Assembly.Load(String('bin/attribute_code_generation_test'))
        x = program.GetType('X')

        attrs = [a for a in x.GetCustomAttributes(False) if 'Thingie' in a.GetType().FullName]
        self.assertNotEqual(0, len(attrs))

if __name__ == '__main__':
    unittest.main()
