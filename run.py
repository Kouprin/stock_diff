import configparser
import os.path
import json
import time

MODULES_DIR = "modules"
DATA_DIR = "data"

class Module(object):

    def __init__(self, module_name):
        self.module_name = module_name
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
            self.ticker_ts = js["timestamp"]
            f.close()
        else:
            self.ticker = self.loadTicker()
            self.ticker_ts = time.time()

    def dumpTicker(self):
        file_name = DATA_DIR + "/" + self.module_name
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
for module in modules:
    print(module.getRate(module.ticker, "USD", "BTC"))
    module.dumpTicker()
print(config.sections())
