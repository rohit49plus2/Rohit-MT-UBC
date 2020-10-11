'''
Created on 2013-02-15

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

from FRLogParser import FRLogParser
from FRSubject import FRSubject

class FRLogAnalyzer(object):
    '''
    classdocs
    '''

    def __init__(self, logger, subjectIds, FRLogsRootPath, computeCustomEmotions):
        '''
        Constructor
        '''
        self.logger = logger
        """logger for system messages"""
        self.subjects = []
        """list of FRSubject elements"""
        self.parser = None
        """parser associated to this analyzer"""
        self.computeCustomEmotions = False
        """boolean indicating whether the custom emotions should be calculated when parsing a subject"""
        
        # Initialize the list of subjects
        for sId in subjectIds:
            self.subjects.append(FRSubject(logger, sId, FRLogsRootPath))
            if not self.subjects[-1].logsAvailable:
                del(self.subjects[-1])
                logger.info("No FaceReader logs found for participant " + str(sId))
            else:
                logger.info("FaceReader logs found for participant " + str(sId))
        logger.info("FaceReader logs found for " + str(len(self.subjects)) + " out of " + str(len(subjectIds)))
        
        # Initialize the parser to be used
        self.parser = FRLogParser()
        self.computeCustomEmotions = computeCustomEmotions
        
    
    def parseSubject(self, subjectID):
        subjectFound = False
        for i, subj in enumerate(self.subjects):
            if subj.ID == subjectID:
                self.logger.info("Parsing FR log for subject " + str(i+1) + " with ID " +  str(subj.ID))
                self.parser.parseLogs(self.logger, subj, self.computeCustomEmotions)
                subjectFound = True
        if not subjectFound:
            self.logger.warning("Couldn't find FR log for subject with ID " + str(subj.ID))
    
    def parseSubjects(self):
        # Parse the logs associated to each subjects
        for i, subj in enumerate(self.subjects):
            self.logger.info("Parsing FR log for subject " + str(i+1) + " with ID " +  str(subj.ID))
            self.parser.parseLogs(self.logger, subj, self.computeCustomEmotions)