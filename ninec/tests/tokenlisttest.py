import unittest

from nine import error
from nine.tokenlist import TokenList

class TokenListTest(unittest.TestCase):
    def setUp(self):
        self.tokenList = TokenList((0,1,2,3,4,5,6,7,8,9))

    def testTokenList(self):
        self.failUnless(self.tokenList is not None)

    def testPeek(self):
        self.failUnless(self.tokenList.peek() == 0)

    def testGetPosition(self):
        self.failUnless(self.tokenList.getPosition() == 0)

    def testSetPosition(self):
        self.tokenList.setPosition(1)
        self.failUnless(self.tokenList.getPosition() == 1)
        self.tokenList.setPosition(0)

    def testGetNext(self):
        self.failUnless(self.tokenList.getNext() == 0)
        self.failUnless(self.tokenList.getPosition() == 1)

    def testExpect(self):
        self.tokenList.expect(0)

        self.failUnlessRaises(
            error.SyntaxError,
            lambda: self.tokenList.expect(0)
        )

        self.tokenList.expect(1)
