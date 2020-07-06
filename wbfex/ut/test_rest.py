'''
Created on Jul 6, 2020

@author: wbfex
'''

from wbfex.wbf_rest import WBFExRest

import unittest


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testDummy(self):
        self.assertFalse('Foo'.isupper())
    def testDummy2(self):
        self.assertTrue('Foo'.isupper())


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()