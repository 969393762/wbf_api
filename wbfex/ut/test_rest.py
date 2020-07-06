'''
Created on Jul 6, 2020

@author: wbfex
'''

from wbfex.wbf_rest import WBFExRest

import unittest


class Test(unittest.TestCase):


    def setUp(self):
        self.rest = WBFExRest(None,None)
        self.oneminute = self.rest.get_ohlcv_data('BTC/USDT')

    def tearDown(self):
        pass


    def test_ohlcv(self):
        self.assertIsNotNone(self.oneminute, 'Should not be none.')
        self.assertEqual(len(self.oneminute), 300, 'Default length is 300 in not empty.')
    
    def test_ohlcv_timestamp(self):
        ts = self.oneminute[0][0]
        self.assertEqual(len(str(ts)), 10, 'Timestamp should be a 10-digit number.')  
    
    def test_ohlcv_numeric(self):
        _, o,h,l,c,_ = self.oneminute[0]
        self.assertTrue(h>=l, 'High should be no less than low.')
        self.assertTrue(o<=h, 'Open should be no greater than high.')
        self.assertTrue(c<=h, 'Close should be no greater than high.')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()