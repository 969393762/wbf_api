import click
import datetime
from configure_symbols import symbols
from wbf_ws import WBFExWebsocket
from functools import reduce

"""""""""""""""""""""""""""""""""
Trade|Depth Data Handler
"""""""""""""""""""""""""""""""""
def handle_simple(channel, data):
    if 'depth' in channel:
        print( data['symbol'], 'bid1:{}, ask1:{}'.format(data['bids'][0], data['asks'][0]) )
    elif 'trade' in channel:
        for d in data:
            di = d['info']
            print( '[trade]', datetime.datetime.fromtimestamp( float(d['timestamp'])/1000), di['side'], d['symbol'], di['price'], di['vol'], di['amount'])

trade_price = 0
def price_control_rise(channel,data):
    global trade_price
    factor = 10/100
    if 'depth' in channel:
        bids = data['bids']
        asks = data['asks']
        if trade_price >0:
            print( asks )
            sub_asks = filter(lambda e:float(e[0])<trade_price*(1+factor), asks)
            print( list(sub_asks) )
            sub_total = reduce(lambda a,b: a[0]*a[1]+b[0]*b[1], sub_asks)
            print(sub_total)
    elif 'trade' in channel:
        for d in data:
            di = d['info']
            trade_price = float(di['price'])
    else:
        pass

"""""""""""""""""""""""""""""""""
Trail run
"""""""""""""""""""""""""""""""""
@click.command()
@click.option('--symbols','symbols',help='Comma-sperated symbols to be monitored.')
def main(symbols):
    wbf_ws = WBFExWebsocket(on_update_trade=price_control_rise, on_update_depth=price_control_rise, ws_symbol=symbols.split(','))
    wbf_ws.start()

if __name__ == '__main__':
    main()
