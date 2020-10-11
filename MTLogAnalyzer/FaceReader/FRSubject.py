'''
Created on 2013-02-15

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

import os

class FRSubject(object):
    '''
    classdocs
    '''

    def __init__(self, logger, ID, FRLogsRootPath):
        '''
        Constructor
        '''
        self.ID = ID
        """ID of the subject"""
        self.stateLog = ""
        """filename and path of the state FaceReader log file"""
        self.detailedLog = ""
        """filename and path of the detailed FaceReader log file"""
        self.logsAvailable = False
        """have both the state and detailed logs have been found for this subject"""
        self.fps = -1
        """number of frames per second in the analyzed video"""
        self.log = []
        
        self.findLogs(logger, FRLogsRootPath)
        self.logsAvailable = (self.detailedLog != "" and self.stateLog != "")
    
    def findLogs(self, logger, FRLogsRootPath):
        cleanId = self.ID[-5:]
        for filfr in os.listdir(FRLogsRootPath):
            if os.path.isfile(FRLogsRootPath + "/" +  filfr):
                with open(FRLogsRootPath + "/" + filfr, 'r') as finfr:
                    # retrieve the participant ID from the calibration file name used on the 4th line of the log file
                    if "pn" in filfr:    # if pn is in the file name, retrieve the participant ID from there
                        participantId = filfr[filfr.index("pn")+2:filfr.index("pn")+2+5]
                    else:
                        finfr.readline()
                        finfr.readline()
                        finfr.readline()
                        participantId = finfr.readline().split("\t")[1][2:7]
                    if participantId == cleanId:
                        if "detailed" in filfr:
                            self.detailedLog = FRLogsRootPath + "/" + filfr        # initialize the name of the FR detailed log file to be analyzed
                        elif "state" in filfr:
                            self.stateLog = FRLogsRootPath + "/" + filfr
                        else:
                            logger.info("Found a FaceReader file corresponding to the subject but which is neither a state or detailed file")