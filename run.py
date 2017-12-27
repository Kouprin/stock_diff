import configparser

class Module(object):

    def __init__(self, module_name):
        self.module_name = module_name
        module_path = "modules." + module_name
        imported = __import__(module_path, fromlist=[None])
        self.load_ticker = getattr(imported, module_name + "LoadTicker")
        self.get_rate = getattr(imported, module_name + "GetRate")
        self.ticker = None

def createModules(config, modules):
    if not 'modules' in config.sections():
        raise("no modules founds")
    for module_name in config['modules']:
        modules.append(Module(module_name))
        #module_path = "modules." + module_name
        #load_methods.append(getattr(imported, module_name + "Load"))
        #get_data_methods.append(getattr(imported, module_name + "GetData"))

config = configparser.ConfigParser()
config.read('config.ini')
modules = []
createModules(config, modules)
print(modules)
for module in modules:
    print(module.get_rate(module.ticker, "USD", "BTC"))
print(config.sections())
