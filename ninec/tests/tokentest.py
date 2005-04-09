import unittest
from nine.token import Token 

class TokenTest(unittest.TestCase):
    def testNewToken(self):
        t = Token('identifier', 'value')
        self.failUnless(t is not None)
        self.failUnless(t.type == 'identifier')
        self.failUnless(t.value == 'value')