
import unittest
from nine.scope import Scope

class Foo:
    pass
foo = Foo()

class ScopeTest(unittest.TestCase):
    def setUp(self):
        self.scope = Scope(parent=None)

    def testNew(self):
        # If execution passes the setUp phase, the test has already passed.
        pass

    def testAddSymbol(self):
        self.scope.addSymbol('foo', foo)

    def testBadAddSymbol(self):
        self.scope.addSymbol('foo', foo)

        self.assertRaises(AssertionError, lambda: self.scope.addSymbol('foo', foo))

    def testSimpleResolve(self):
        self.scope.addSymbol('foo', foo)
        self.assertEqual(self.scope.resolveSymbol('foo'), foo)

    def testNestedResolve(self):
        scope2 = Scope(parent=self.scope)
        self.scope.addSymbol('foo', foo)

        result = scope2.resolveSymbol('foo')
        self.assertEqual(foo, result)

if __name__ == '__main__':
    unittest.main()
