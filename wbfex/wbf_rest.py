"""
2018-08-08

status: prod
"""
import time
import requests
import hashlib
import datetime
ROOT_URL = "https://openapi.wbf.info"
"""
# In case of the url above is blocked use following instead:
ROOT_URL = "https://openapi.wbf.live"
"""

class WBFExRest:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
    def symbol(self,symbol):
        return symbol.replace('/','').lower()
    def sign(self,dic):
        tmp=''
        for key in sorted(dic.keys()):
            tmp+=key+str(dic[key])
        tmp+=self.api_secret
        sign=hashlib.md5(tmp.encode()).hexdigest()
        return sign

    def get_ohlcv_data(self, symbol, timeframe=1):
        url="{}/open/api/get_records".format(ROOT_URL)
        r=requests.get(url,params={'symbol':self.symbol(symbol),'period':timeframe})
        return r.json()['data']

    def get_ticker_data(self, symbol):
        url="{}/open/api/get_ticker".format(ROOT_URL)
        r=requests.get(url,params={'symbol':self.symbol(symbol)})
        response = r.json()['data']
        result = {
            'ask': response['sell'],
            'bid': response['buy'],
            'close': response['last'],
            'high': 0,
            'low': 0,
            'last': response['last'],
            'price': response['last'],
            'amount': response['vol'],
            'symbol':symbol
        }
        return result

    def get_depth_data(self, symbol):
        url="{}/open/api/market_dept".format(ROOT_URL)
        r=requests.get(url,params={'symbol':self.symbol(symbol),'type':'step0'})
        response=r.json()['data']['tick']
        response['symbol']=symbol
        response['symbol_name'] = symbol
        response['data_type'] = 'depth'
        return response

    def get_balance(self):
        url="{}/open/api/user/account".format(ROOT_URL)
        dic={'api_key':self.api_key,'time':time.time()}
        dic['sign']=self.sign(dic)
        r=requests.get(url,params=dic)
        returndic = {}
        balance_data = r.json()['data']['coin_list']
        balance_dic = {}
        for coin_i in balance_data:
            coin_vol = float(coin_i['locked'])+float(coin_i['normal'])
            if abs(coin_vol-0)>1e-7:
                balance_dic[coin_i['coin'].upper()]=coin_vol
                returndic[coin_i['coin'].upper()] = {'total': coin_vol, 'free': float(coin_i['normal']),
                                                     'used': float(coin_i['locked'])}
        returndic['total'] = balance_dic
        return returndic

    def limit_place_buy_order(self, symbol, price, amount):
        url="{}/open/api/create_order".format(ROOT_URL)
        
        params = {
            'api_key':self.api_key,
            'time':time.time(),
            'symbol':self.symbol(symbol),
            'side':'BUY',
            'type':1,
            'volume':amount,
            'price':price,
            
        }
        params['sign']=self.sign(params)
        time1= time.time()
        response=requests.post(url,data=params)
        if response.status_code != 200:
            raise requests.exceptions.HTTPError
        else:
            jsonstr = response.json()
            if 'code' in jsonstr and int(jsonstr['code']) != 0:
                raise "place order failed : {}".format(jsonstr['msg'])

            elif jsonstr['msg'] == 'suc' and int(jsonstr['code']) == 0:
                return self._parse_order_insertorder(self._parse_open_order(jsonstr['data'], symbol), symbol, 'buy')
            else:
                raise "place order failed : {}".format(jsonstr['msg'])

    def limit_place_sell_order(self, symbol, price, amount):
        url="{}/open/api/create_order".format(ROOT_URL)
        
        params = {
            'api_key':self.api_key,
            'time':time.time(),
            'symbol':self.symbol(symbol),
            'side':'SELL',
            'type':1,
            'volume':amount,
            'price':price,
            
        }
        params['sign']=self.sign(params)
        response=requests.post(url,data=params)
        if response.status_code != 200:
            raise requests.exceptions.HTTPError
        else:
            jsonstr = response.json()
            if 'code' in jsonstr and int(jsonstr['code']) != 0:
                raise "place order failed : {}".format(jsonstr['msg'])
            elif jsonstr['msg'] == 'suc' and int(jsonstr['code']) == 0:
                return self._parse_order_insertorder(self._parse_open_order(jsonstr['data'], symbol), symbol, 'sell')
            else:
                raise "place order failed : {}".format(jsonstr['msg'])
    def iso8601(self,timestamp=None):
        if timestamp is None:
            return timestamp
        if not isinstance(timestamp, int):
            return None
        if int(timestamp) < 0:
            return None
        try:
            utc = datetime.datetime.utcfromtimestamp(timestamp // 1000)
            return utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-6] + "{:03d}".format(int(timestamp) % 1000) + 'Z'
        except (TypeError, OverflowError, OSError):
            return None
    def _parse_order(self, order_response, symbol):
        id = None
        timestamp = None
        datetime = None
        lastTradeTimestamp = None
        status = None
        symbol = symbol
        type = None
        side = None
        price = None
        amount = None
        filled = None
        remaining = None
        trades = None
        fee = None
        avgprice = None

        info = None

        if 'id' in order_response:
            id = order_response['id']
        if 'created_at' in order_response:
            datetime = self.iso8601(int(order_response['created_at']))
            timestamp = order_response['created_at']
        symbol = symbol
        if 'status_msg' in order_response:
            p_state = order_response['status_msg']
            if p_state == '完全成交':
                status = 'closed'
            elif p_state == '未成交' or p_state == '待撤单' or p_state == '部分成交':
                status = 'open'
            elif p_state == '已撤单':
                status = 'canceled'
        type = 'limit'
        if "side" in order_response:
            position = order_response["side"]
            if 'SELL' in position:
                side = 'sell'
            else:
                side = 'buy'
        if "price" in order_response:
            price = float('%.8f' % float(order_response["price"]))
        if "deal_price" in order_response:
            avgprice = float('%.8f' % float(order_response["deal_price"]))
        if "volume" in order_response:
            amount = float('%.8f' % float(order_response["volume"]))
        if "remain_volume" in order_response:
            remaining = float('%.8f' % float(order_response["remain_volume"]))
        if remaining is not None and amount is not None:
            filled = amount - remaining
        if "deal_volume" in order_response:
            filled = float('%.8f' % float(order_response["deal_volume"]))
            remaining = amount - filled
        if 'fee' in order_response:
            fee_s = float('%.8f' % float(order_response["fee"]))
            if side == 'buy':
                fee = {'base': fee_s, 'quote': 0}
            else:
                fee = {'base': 0, 'quote': fee_s}
        return {
            'id': id,
            'timestamp': timestamp,
            'datetime': datetime,
            'lastTradeTimestamp': None,
            'status': status,
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'trades': None,
            'fee': fee,
            'avgprice': avgprice,

            'info': order_response,
        }


    def _parse_open_order(self, order_response, symbol):
        id = None
        timestamp = None
        datetime = None
        lastTradeTimestamp = None
        status = None
        symbol = symbol
        type = None
        side = None
        price = None
        amount = None
        filled = None
        remaining = None
        trades = None
        fee = None
        avgprice = None

        info = None

        if 'order_id' in order_response:
            id = order_response['order_id']
        if 'created_at' in order_response:
            datetime = self.iso8601(int(order_response['created_at']))
            timestamp = order_response['created_at']
        symbol = symbol
        if 'status_msg' in order_response:
            p_state = order_response['status_msg']
            if p_state == '未成交':
                status = 'closed'
            elif p_state == '未成交' or p_state == '待撤单':
                status = 'open'
            elif p_state == '已撤单':
                status = 'canceled'
        type = 'limit'
        if "type" in order_response:
            position = order_response["type"]
            if 'buy' in position:
                side = 'buy'
            else:
                side = 'sell'
        if "price" in order_response:
            price = float('%.8f' % float(order_response["price"]))
        if "deal_price" in order_response:
            avgprice = float('%.8f' % float(order_response["deal_price"]))
        if "volume" in order_response:
            amount = float('%.8f' % float(order_response["volume"]))
        if "remain_volume" in order_response:
            remaining = float('%.8f' % float(order_response["remain_volume"]))
        if remaining is not None and amount is not None:
            filled = amount - remaining
        if "deal_volume" in order_response:
            filled = float('%.8f' % float(order_response["deal_volume"]))
            remaining = amount - filled
        if 'fee' in order_response:
            fee_s = float('%.8f' % float(order_response["fee"]))
            if side == 'buy':
                fee = {'base': fee_s, 'quote': 0}
            else:
                fee = {'base': 0, 'quote': fee_s}
        return {
            'id': id,
            'timestamp': timestamp,
            'datetime': datetime,
            'lastTradeTimestamp': None,
            'status': status,
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'trades': None,
            'fee': fee,
            'avgprice': avgprice,

            'info': order_response,
        }


    def get_order_msg_byid(self, symbol, order_id):
        response = ''
        try:
            url = "{}/open/api/order_info".format(ROOT_URL)

            params = {
                'api_key': self.api_key,
                'time': int(1000 * time.time()),
                'symbol': self.symbol(symbol),
                'order_id': order_id,
            }
            params['sign'] = self.sign(params)
            s = ''
            for key in sorted(params.keys()):
                s += key + '=' + str(params[key]) + '&'
            s = s[:-1]
            s = '?' + s
            time1 = time.time()
            r = requests.get(url + s)
            response = r.json()
            if 'msg' in response and response['msg']=='suc':
                return self._parse_order(response['data']['order_info'],symbol)
            else:
                raise requests.exceptions.HTTPError
        except Exception as e:
            self.client_normal=False
            raise requests.exceptions.HTTPError
    def cancel_order_byid(self, symbol, order_id):
        url="{}/open/api/cancel_order".format(ROOT_URL)

        params = {
            'api_key':self.api_key,
            'time':int(time.time()*1000),
            'symbol':self.symbol(symbol),
            'order_id':order_id,
        }
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'postman-token': "40ff9187-ba33-bfb3-024f-fb4d05b437d6"
            }
        params['sign']=self.sign(params)
        s=''
        for key in sorted(params.keys()):
            s+=key+'='+str(params[key])+'&'
        s=s[:-1]
        time1= time.time()
        r=requests.post(url,data=s,headers=headers)
        response = r.json()
        if 'code' in response and int(response['code'])==8:
            raise response['msg']
    def get_open_orders_bysymbol(self, symbol):
        url="{}/open/api/v2/new_order".format(ROOT_URL)
        
        params = {
            'api_key':self.api_key,
            'time':int(1000*time.time()),
            'symbol':self.symbol(symbol),
        }
        params['sign']=self.sign(params)
        s=''
        for key in sorted(params.keys()):
            s+=key+'='+str(params[key])+'&'
        s=s[:-1]
        s='?'+s
        r=requests.get(url+s)
        return r.text
    def _parse_order_insertorder(self, ordermsg, symbol, side):
        ordermsg['symbol'] = symbol
        ordermsg['side'] = side
        if 'id' in ordermsg and ordermsg['id'] is not None:
            if 'status' in ordermsg:
                ordermsg['msg'] = ordermsg['status']
            else:
                ordermsg['msg'] = None
        else:
            ordermsg['id'] = None
            ordermsg['msg'] = None
        return ordermsg
    def cancel_open_orders_bysymbol(self, symbol):
        url="{}/open/api/cancel_order_all".format(ROOT_URL)
        
        params = {
            'api_key':self.api_key,
            'time':int(1000*time.time()),
            'symbol':self.symbol(symbol),
        }
        params['sign']=self.sign(params)
        s=''
        for key in sorted(params.keys()):
            s+=key+'='+str(params[key])+'&'
        s=s[:-1]
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'postman-token': "40ff9187-ba33-bfb3-024f-fb4d05b437d6"
            }
        r=requests.post(url,data=s,headers=headers)
        return r.text

    def get_all_trades_bysymbol(self, symbol, startDate=None, endDate=None):
        url = "{}/open/api/all_trade".format(ROOT_URL)
        params = {
            'api_key': self.api_key,
            'time': int(1000 * time.time()),
            'symbol': self.symbol(symbol),
            'sort': 1,
            'pageSize': 50000,

        }
        if startDate:
            params['startDate'] = startDate
        if endDate:
            params['endDate'] = endDate
        params['sign'] = self.sign(params)
        s = ''
        for key in sorted(params.keys()):
            s += key + '=' + str(params[key]) + '&'
        s = s[:-1]
        s = '?' + s
        r = requests.get(url + s)
        return r.json()


if __name__ == '__main__':
    ak, sk = '',''
    ex = WBFExRest(ak, sk)
