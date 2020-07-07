import click
import datetime
from wbf_ws import WBFExWebsocket
from functools import reduce

def _f( float_v):
    return int(float_v*100)/100

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

def depth_stat(channel, data):
    if 'depth' in channel:
        a,b = data['asks'],data['bids']
        md = float(a[0][0])*.5 + float(b[0][0])*.5

        pct = 10
        md_up = md*(1+pct/100)
        md_down = md*(1-pct/100)

        amt,vol=0,0
        for e in a:
            if float(e[0])< md_up:
                amt += e[1]
                vol += e[0]*e[1]
            else: break
        ask_pct = (amt,vol)

        amt,vol=0,0
        for e in b:
            if float(e[0])>md_down:
                amt += e[1]
                vol += e[0]*e[1]
            else: break
        bid_pct = (amt,vol)

        print(f'[depth {pct/100}] amt:{_f(ask_pct[0]),_f(bid_pct[0]),_f(ask_pct[0]+bid_pct[0])}    vol:{_f(ask_pct[1]),_f(bid_pct[1]),_f(ask_pct[1]+bid_pct[1])}')


RISE_PRICE_CAP=-1
RISE_FACTOR=-1

def price_control_rise(channel,data):
    factor = 3/100

    if 'depth' in channel:
        bids = data['bids']
        asks = data['asks']
        trade_price  = float(bids[0][0])*.5 + float(asks[0][0])*.5
        if trade_price >0:
            if RISE_FACTOR:
                price_cap = trade_price*(1+float(RISE_FACTOR)/100)
            elif RISE_PRICE_CAP:
                price_cap = float(RISE_PRICE_CAP)
            else:
                pass
            sub_asks = filter(lambda e:float(e[0])<= price_cap, asks )

            sub_asks = map(lambda e: [float(e[0]), float(e[1])], sub_asks )
            t, v = 0,0
            for e in sub_asks:
                t += e[0]*e[1]
                v += e[1]
            print( f'cost: {t}u to pull up to ${price_cap} {(price_cap-trade_price)/trade_price*100}% @{trade_price}' )
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
    wbf_ws = WBFExWebsocket(
            on_update_trade=depth_stat, #price_control_rise, #handle_simple,
            on_update_depth=depth_stat, #price_control_rise, #handle_simple,
            ws_symbol=symbols.split(','))
    wbf_ws.start()

if __name__ == '__main__':
    main()

