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
RISE_PRICE_CAP=-1
RISE_FACTOR=-1

def price_control_rise(channel,data):
    global trade_price
    factor = 3/100

    if 'depth' in channel:
        bids = data['bids']
        asks = data['asks']
        if trade_price >0:
            if RISE_FACTOR:
                price_cap = trade_price*(1+float(RISE_FACTOR)/100)
            elif RISE_PRICE_CAP:
                price_cap = float(RISE_PRICE_CAP)
            else:
                pass
            sub_asks = filter(lambda e:float(e[0])< price_cap, asks )

            sub_asks = map(lambda e: [float(e[0]), float(e[1])], sub_asks )
            t, v = 0,0
            for e in sub_asks:
                t += e[0]*e[1]
                v += e[1]
            print( t, price_cap )

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
@click.option('--rise_cap', 'rise_cap', help='rise cap')
@click.option('--rise_factor', 'rise_factor', help='rise factor')
def main(symbols, rise_cap, rise_factor):
    global RISE_FACTOR,RISE_PRICE_CAP
    RISE_PRICE_CAP = rise_cap
    RISE_FACTOR = rise_factor
    wbf_ws = WBFExWebsocket(on_update_trade=price_control_rise, on_update_depth=price_control_rise, ws_symbol=symbols.split(','))
    wbf_ws.start()

if __name__ == '__main__':
    main()
