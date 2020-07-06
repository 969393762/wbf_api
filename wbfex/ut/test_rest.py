'''
Created on Jul 6, 2020

@author: wbfex
'''

from wbfex.wbf_rest import WBFExRest

import unittest


class Test(unittest.TestCase):


    def setUp(self):
        self.symbol = 'BTC/USDT'
        self.onehour = WBFExRest.get_ohlcv_data(self.symbol, 60)

    def tearDown(self):
        pass


    def test_ohlcv(self):
        self.assertIsNotNone(self.onehour, 'Should not be none.')
        self.assertEqual(len(self.onehour), 300, 'Default length is 300 in not empty.')
    
    def test_ohlcv_timestamp(self):
        ts = self.onehour[0][0]
        self.assertEqual(len(str(ts)), 10, 'Timestamp should be a 10-digit number.')  
    
    def test_ohlcv_numeric(self):
        _, o,h,l,c,_ = self.onehour[0]
        self.assertTrue(h>=l, 'High should be no less than low.')
        self.assertTrue(o<=h, 'Open should be no greater than high.')
        self.assertTrue(c<=h, 'Close should be no greater than high.')
        
    def test_ohlcv_timeframe(self):
        ts0,_,_,_,_,_ = self.onehour[0]
        ts1,_,_,_,_,_ = self.onehour[1]
        self.assertEqual(ts1-ts0, 3600, "1-hour candlestick lines should have a gap of 3600 seconds, or 1 hour.")
        
    def test_ticker_data(self):
        self.ticker = WBFExRest.get_ticker_data(self.symbol)
        self.assertTrue( all(map(lambda s: s in self.ticker.keys(),['ask','bid', 'price','amount','symbol'] )), 'Missing keys in the return values.')
        
        bid,ask = self.ticker['bid'], self.ticker['ask']
        self.assertTrue(ask>bid, 'Ask price must be higher than bid price.')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()