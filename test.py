import api.poloniex as poloniex
import api.kraken as kraken
import pprint

print(poloniex.poloniexGetData())
raise

p = poloniex.poloniex(0, 0)
pp = pprint.PrettyPrinter(indent=4)
pp.pprint("poloniex " + p.api_query("returnTicker")["USDT_BTC"]['last'])

k = kraken.API()
open_positions = k.query_public('Ticker', {'pair':'XXBTZUSD'})
pp.pprint("kraken " + open_positions['result']['XXBTZUSD']['c'][0])
