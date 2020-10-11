'''
Created on 5 avr. 2011

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

import logging

class Logger():
    """Configure the logging level for the application"""
    # associated names for the different logging levels usable here
    LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}
    
    logger = None
    
    def __init__(self, level):
        loglevel = self.LEVELS.get(level, logging.NOTSET)   # set the logging level
        #logging.basicConfig(level=loglevel)
        self.logger = logging.getLogger("loganalyzer")      # create logger
        self.logger.setLevel(loglevel)
        
        ch = logging.StreamHandler()                        # create console handler and set level to debug
        ch.setLevel(loglevel)
                
        formatter = logging.Formatter("%(levelname)-8s: %(message)s") # create formatter
        #%(asctime)s - %(name)s 
        
        ch.setFormatter(formatter)                          # add formatter to ch
        self.logger.addHandler(ch)                          # add ch to logger
        
        #return logger