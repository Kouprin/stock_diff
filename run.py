import configparser
import os.path
import json
import time

MODULES_DIR = "modules"
DATA_DIR = "data"

class Module(object):

    def __init__(self, module_name):
        self.name = module_name
        module_path = MODULES_DIR + "." + module_name
        imported = __import__(module_path, fromlist=[None])
        self.loadTicker = getattr(imported, module_name + "LoadTicker")
        self.getRate = getattr(imported, module_name + "GetRate")
        self.ticker = None
        self.ticker_ts = 0
        file_name = DATA_DIR + "/" + module_name
        if os.path.isfile(DATA_DIR + "/" + module_name):
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

def createModules(config, modules):
    if not 'modules' in config.sections():
        raise("no modules founds")
    for module_name in config['modules']:
        modules.append(Module(module_name))

config = configparser.ConfigParser()
config.read('config.ini')
modules = []
createModules(config, modules)
print(modules)
update_period = int(config['update']['default'])
for module in modules:
    print("Running module: " + module.name)
    print("Ticker timestamp is: " + str(module.ticker_ts))
    current_update = update_period
    if module.name in config['update']:
        current_update = int(config['update'][module.name])
        print("Found specified refresh time: " + str(current_update))
    if current_update + module.ticker_ts < time.time():
        print("Ticker updated is required, current time is: ", time.time())
        for x in range(1, 5):
            print("Trying to download a ticker, attemption: ", x)
            module.ticker = module.loadTicker()
            module.ticker_ts = time.time()
            if module.ticker != None:
                break
            time.sleep(3)
        if module.ticker == None:
            print("Unable to get a ticker from: " + module.name)
            continue

    print("Okay, getting rates")
    print(module.getRate(module.ticker, "USD", "BTC"))

    print("Dumping a ticker for: " + module.name)
    module.dumpTicker()
