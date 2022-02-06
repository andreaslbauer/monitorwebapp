import logging

class ConfigInfo:

    # singleton instance
    configInfo = None
    configFilename = 'monitorappconfig.txt'

    def __init__(self):
        self.timeBetweenUpdates = 15
        self.chartShowNumberSamples = 480
        self.chartInterleave = 60

    # load data from persistent store
    def load(self):
        try:
            file = open(self.configFilename, "r")
            self.timeBetweenUpdates = int(file.read())
            self.chartShowNumberSamples = int(file.read())
            self.chartInterleave = int(file.read())
            file.close()
            logging.info("Read update interval: %i from file %s", self.timeBetweenUpdates, self.configFilename)

        except:
            logging.info("Unable to read configuration file %s", self.configFilename)
            pass

    # load data from persistent store
    def store(self):
        file = open(self.configFilename, "w")
        file.write(str(self.timeBetweenUpdates))
        file.write(str(self.chartShowNumberSamples))
        file.write(str(self.chartInterleave))
        file.close()

ConfigInfo.configInfo = ConfigInfo()
ConfigInfo.configInfo.load()