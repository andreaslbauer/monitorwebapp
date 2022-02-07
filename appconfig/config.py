import logging
import pickle

class ConfigInfo:

    # singleton instance
    configInfo = None
    configFilename = 'monitorapp.cfg'

    def __init__(self):
        self.timeBetweenUpdates = 15
        self.chartShowNumberSamples = 480
        self.chartInterleave = 60

    # load data from persistent store
    def load(self):
        try:
            file = open(self.configFilename, "rb")
            tempdict = pickle.load(file)
            self.__dict__.update(tempdict)
            file.close()
            logging.info("Read update interval: %i from file %s", self.timeBetweenUpdates, self.configFilename)

        except:
            logging.info("Unable to read configuration file %s", self.configFilename)
            pass

    # load data from persistent store
    def store(self):
        file = open(self.configFilename, "wb")
        pickle.dump(self.__dict__, file, 2)
        file.close()

ConfigInfo.configInfo = ConfigInfo()
ConfigInfo.configInfo.load()