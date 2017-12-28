import configparser
import os.path
import json
import time

MARKETS_DIR = "markets"
DATA_DIR = "data"

class Market(object):

    def __init__(self, market_name):
        self.name = market_name
        market_path = MARKETS_DIR + "." + market_name
        imported = __import__(market_path, fromlist=[None])
        self.loadTicker = getattr(imported, market_name + "LoadTicker")
        self.getRate = getattr(imported, market_name + "GetRate")
        self.ticker = None
        self.ticker_ts = 0
        file_name = DATA_DIR + "/" + market_name
        if os.path.isfile(DATA_DIR + "/" + market_name):
            f = open(file_name, 'r')
            js = json.load(f)
            self.ticker = js["ticker"]
            self.ticker_ts = int(js["timestamp"])
            f.close()
        else:
            self.ticker = self.loadTicker()
            self.ticker_ts = int(time.time())

    def dumpTicker(self):
        file_name = DATA_DIR + "/" + self.name
        f = open(file_name, 'w')
        json.dump({"timestamp" : self.ticker_ts, "ticker" : self.ticker}, f)
        f.close()

class Suggestion(object):

    def __init__(self, market_from, market_to, coin, mediator, income):
        self.market_from = market_from
        self.market_to = market_to
        self.coin = coin
        self.mediator = mediator
        self.income = income


def createMarkets(config, markets):
    for market_name in config['markets']:
        markets.append(Market(market_name))

def getSuggestions(markets, coins, mediators, suggestions):
    print(" === ")
    print("Okay, getting suggestions")
    for market_from in markets:
        for market_to in markets:
            if market_from == market_to:
                continue
            for mediator in mediators:
                mediator = mediator.upper()
                rate = float(mediators[mediator])
                for coin in coins:
                    coin = coin.upper()
                    if mediator == coin:
                        continue
                    # the idea is to take "coin" from "market_from" then use "mediator" as temporary currency
                    # and then buy "coin" at "market_to" for "suggestion" currency again
                    #
                    # so we just need to perform two transactions using "mediator" as an intermediary
                    value_from = market_from.getRate(market_from.ticker, coin, mediator)
                    value_to = market_to.getRate(market_to.ticker, mediator, coin)
                    if value_from != None and value_to != None:
                        value_from = float(value_from)
                        value_to = float(value_to)
                        if value_from - value_to > rate:
                            suggestions.append(Suggestion(market_from, market_to, coin, mediator, value_from - value_to))

config = configparser.ConfigParser()
config.read('config.ini')
markets = []
createMarkets(config, markets)
update_period = int(config['update']['default'])
for market in markets:
    print("Running market: " + market.name)
    print("Ticker timestamp is: " + str(market.ticker_ts))
    current_update = update_period
    if market.name in config['update']:
        current_update = int(config['update'][market.name])
        print("Found specified refresh time: " + str(current_update))
    if current_update + market.ticker_ts < time.time():
        print("Ticker updated is required, current time is:", time.time())
        for x in range(1, 5):
            print("Trying to download a ticker, attemption:", x)
            market.ticker = market.loadTicker()
            market.ticker_ts = time.time()
            if market.ticker != None:
                break
            time.sleep(3)
        if market.ticker == None:
            print("Unable to get a ticker from: " + market.name)
            continue

    #print(market.getRate(market.ticker, "USD", "BTC"))

    print("Dumping a ticker for: " + market.name)
    market.dumpTicker()

suggestions = []
getSuggestions(markets, config['coins'], config['suggestions'], suggestions)
for suggestion in suggestions:
    print("Sell", suggestion.coin, "for", suggestion.mediator, "on", suggestion.market_from.name, "then buy it on", suggestion.market_to.name, "- it gives you", suggestion.income, suggestion.mediator, "per each", suggestion.coin)
