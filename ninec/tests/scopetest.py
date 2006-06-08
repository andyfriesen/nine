
import unittest
from nine.scope import Scope

class Foo:
    pass
foo = Foo()
bar = Foo()

class ScopeTest(unittest.TestCase):
    def setUp(self):
        self.scope = Scope(parent=None)

    def testCtor(self):
        # If execution passes the setUp phase, the test has already passed.
        pass

    def testAddSymbol(self):
        self.scope.addSymbol('foo', foo)

    def testBadAddSymbol(self):
        self.scope.addSymbol('foo', foo)

        self.assertRaises(
            AssertionError,
            lambda: self.scope.addSymbol('foo', foo)
        )

    def testSimpleResolve(self):
        self.scope.addSymbol('foo', foo)
        self.assertEqual(foo, self.scope.resolveSymbol('foo'))

    def testNestedResolve(self):
        scope2 = Scope(parent=self.scope)
        self.scope.addSymbol('foo', foo)
        scope2.addSymbol('bar', bar)

        result = scope2.resolveSymbol('bar')
        self.assertEqual(bar, result)

        result = self.scope.resolveSymbol('bar')
        self.assertEqual(None, result)

if __name__ == '__main__':
    unittest.main()
