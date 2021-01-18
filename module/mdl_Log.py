import logging
import os

class Log(object):
    def __init__(self, logFile):
        if not os.path.isfile(logFile):
            os.system(r"touch {}".format(logFile))
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.INFO)
        # self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        dateFormat = '%H:%M:%S'
        self.formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s', dateFormat)
        self.handler = logging.FileHandler(logFile)
        self.handler.setLevel(logging.INFO)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        
    def LOGE(self, errorMsg):
        self.logger.error(errorMsg)
    
    def LOGW(self,warningMsg):
        self.logger.warning(warningMsg)

    def LOGI(self, infoMsg):
        self.logger.info(infoMsg)
    
    def LOGD(self,debugMsg):
        self.logger.debug(debugMsg)
        
if __name__ == '__main__':
    logFile = "../data/exec.Log"
    if not os.path.isfile(logFile):
        os.system(r"touch {}".format(logFile))
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(logFile)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("Start print log")
    
    