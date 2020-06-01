# WBFex Quantative Trading APIs/SDK
## RESTful APIs
文件内 WBFRest 类包含rest 公共接口和私有接口。公共接口不需要apikey 和 secretkey 即可调用，私有接口需要申请apikey， wbf 交易所官方网站 https://www.wbf.live/ 。

(注：所有接口参考ccxt 格式封装，入参 symbol 格式 BTC/USDT)
### 公共数据访问接口
1.  get_ohlcv_data(self, symbol, timeframe=1)
     * 获取指定交易对 k线数据, timeframe k线时间，1为1m 
2.  get_ticker_data(self, symbol)
     * 获取指定交易对最新成交价
3.  get_depth_data(self, symbol)
     * 获取指定交易对深度数据
     
### 签名函数  
1.  sign(self,dic)

### 私有数据访问接口
1.  get_balance(self)
     * 获取账户余额
2.  limit_place_buy_order(self, symbol, price, amount)
     * 指定交易对限价买单
     * symbol:指定交易对名称
     * price: 下单价格
     * amount: 下单数量
3.  limit_place_sell_order(self, symbol, price, amount)
     * 指定交易对限价卖单
     * symbol:指定交易对名称
     * price: 下单价格
     * amount: 下单数量
4.  get_order_msg_byid(self, symbol, order_id)
     * 按订单号查询指定交易对 订单详情
     * symbol:指定交易对名称
     * order_id: 订单id
5.  cancel_order_byid(self, symbol, order_id)
     * 按订单号撤销指定交易对订单
     * symbol:指定交易对名称
     * order_id: 订单id
6.  get_open_orders_bysymbol(self, symbol)
     * 查询指定交易对所有挂单信息
     * symbol:指定交易对名称
7.  cancel_open_orders_bysymbol(self, symbol)
     * 撤销指定交易对所有挂单
     * symbol:指定交易对名称

8.  get_all_trades_bysymbol(self, symbol, startDate=None, endDate=None)
     * 查询指定交易对成交订单信息
     * startDate: 查询起始时间 ，比如：2020-06-01 18:32:27
     * endDate: 查询结束时间
     
## Websocket API
目前支持：接收深度和最新成交。
### 调用方法
1.  ```wbf_ws = WBFWs(update_data=fun, ws_symbol=['BTC/USDT','ETH/USDT'])```

    ```wbf_ws.start()```
     * ws_symbol:需要接收数据的交易对名称。例如:ws_symbol=['BTC/USDT','ETH/USDT']
