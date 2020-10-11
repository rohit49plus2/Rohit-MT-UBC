'''
Created on 2013-02-15

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''
import recordtype
import os
import pickle, json
import csv
import datetime
from Events import *
from MTSubject import MTSubject
from MTLogParserTimeIntervals2 import MTLogParser # NJ CHANGED from MTLogParser
from Log import Logger
from Utils import *
from EyeTracker.ETLogParser import ETLogParser
#from MetaTutor import Utils
from recordtype import  *  # for recordtype elements, which are mutable version of namedtuples

class MTLogAnalyzer(object):
    """Analyzer of logs information"""
    versionsSupported = ["1.1.16", "1.1.17", "1.1.18", "1.1.20", "1.1.21", "1.2.8", "1.3.2.2", "1.3.3.1" ,"1.3.4.0","1.4.9.8"]
    """versions of MetaTutor logs supported by the analyzer"""
    summaryLogLevelOfDetails = [0, 0, 0, 0, 1, 2, 2, 2, 2,2]
    """amount of information kept in the log, one number per version in versionsSupported.
    Before 1.1.21, the day 1 didn't have a questionnaire about the subject."""
    tabSubjectsInfo = map(lambda x:[x], ["SubjectID", "SubjectName", "Gender", "Age", "Ethnicity", "Education", "GPA", "Major", "School", "# Courses", "Experimenter1", "Experimenter2"])
    """table of information about the subjects, initialized with row names"""
    #subjectsFields = ["SubjectID", "SubjectName", "Gender", "Age", "Ethnicity", "Education", "GPA", "Major", "School", "Experimenter1", "Experimenter2"]
    dictSubjDataType = {"subject":              ["Sub", ["Name", "Gender", "Age", "Ethnicity", "Education", "GPA", "Major", "School", "#Courses"]],
                                "experiment":           ["Exp", ["Experimenter 1", "Experimenter 2", "Day1 log file", "Day2 log file"]],
                                "pagesViewEvents":   ["Pag", ["1st page viewed", "Start time", "2nd page viewed", "Start time", "3rd page viewed", "Start time", "..."]],
                                "allEvents":               ["All", ["Event 1", "Event 2", "Event 3", "..."] ],
                                "SRLEvents":             ["SRL", ["PLAN", "SUMM", "TN", "MPTG", "RR", "COIS", "PKA", "JOL", "FOK", "CE", "INF", "DEPENDS", "Unknown"]]
                                }
    """dictionary of suffixes for the name of files used to store different kind of information about subjects, and column titles for the content of those files"""
    matPageSubgoalStudy23 = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0.5, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0, 0, 0],
                      [0.5, 0.5, 0, 1, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0.5, 0.5, 0, 1, 1, 1, 1, 1, 0.5, 0.5, 0, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0.5, 0.5, 0.5, 0.5, 0, 0, 0.5, 0, 0, 0, 0.5, 0, 0.5, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0.5, 0.5, 0.5, 0, 0, 0, 0.5, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                      [0, 0, 0.5, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                      [1, 1, 1, 0, 0.5, 0.5, 1, 0, 0, 0, 0.5, 0.5, 0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0, 0, 0.5, 0.5, 0.5, 1, 0.5, 1, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]
                      ]
    """7x41 matrix of relevant pages per subgoal (pages from 0 to 40) for studies 2 and 3"""
    matPageSubgoalStudy4 = [[0,0,0,0,1,0,0,0,0,0,0,0,0,1,1,1,1,1,0.5,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0.5,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0.5,0,0,0],
                                [0.5,0.5,0,1,0.5,0,0,0,0,0,0,0,0,0.5,0.5,0.5,0,1,1,1,0.5,0.5,0,0.5,0.5,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0.5,0.5,0.5,0.5,0,0,0.5,0,0,0,0.5,0,0.5,1,1,1,1,1,1,0,0,0,0.5,0.5,0.5,0,0,0,0.5,0,0,0,0,0,1,1,0,0],
                                [0,0,0.5,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0.5,0,0,0,0,0,0,0,0,0,0.5,0,1,1,1,1,1,0,0,0,0],
                                [1,1,1,0,0.5,0.5,1,0,0,0,0.5,0.5,0,0.5,0.5,0.5,0.5,0.5,0,0,0,0,0.5,0.5,0.5,1,0.5,1,0.5,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0.5,0,0,0,0,0,0,0,0,0,0,0,0,0.5,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0],
                                ]
    """7x38 matrix of relevant pages per subgoals (pages from 0 to 37) for study 4"""
    matPageSubgoalDict = {"MT2":matPageSubgoalStudy23, "MT3":matPageSubgoalStudy23, "MT4":matPageSubgoalStudy4, "MT4.5":matPageSubgoalStudy4}
    """dictionary linking the value of subject.study with the correct relevance matrix for that study"""
    maxNbRelevantPagesPerSubgoalStudy23 = map(lambda x:sum(x), [[1 if y>0 else 0 for y in row] for row in matPageSubgoalStudy23])
    """list of 7 values corresponding to the number of pages relevant to each of the subgoals in studies 2 and 3"""
    maxNbRelevantPagesPerSubgoalStudy4 = map(lambda x:sum(x), [[1 if y>0 else 0 for y in row] for row in matPageSubgoalStudy4])
    """list of 7 values corresponding to the number of pages relevant to each of the subgoals in study 4"""
    maxNbRelevantPagesPerSubgoal = {"MT2":matPageSubgoalStudy23, "MT3":matPageSubgoalStudy23, "MT4":matPageSubgoalStudy4, "MT4.5":matPageSubgoalStudy4}
    """dictionary linking the value of subject.study with the correct number of pages relevant to each subgoal for that study"""
    nbPagesInSystem = {"MT2":41, "MT3":41, "MT4":38, "MT4.5":38}
    """dictionary linking the value of subject.study with the total number of pages in the system for that study"""

    matTestPageStudy23 = [[38, 2, 37, 4, 4, 4, 21, 6, 7, 20, 35, 6, 11, 33, 2, 34, 7, 0, 22, 7, 16, 5, 3, 15, 9],              # version A
                                        [12, 1, 0, 5, 15, 16, 3, 18, 15, 23, 13, 12, 14, 13, 29, 32, 36, 2, 2, 29, 31, 10, 24, 40, 2]]  # version B
    """2x25 matrix of page IDs associated to each question of tests A and B for studies 2 and 3"""
    matTestPageStudy4 =   [[35, 2, 34, 4, 4, 4, 19, 6, 7, 19, 32, 6, 11, 30, 2, 31, 7, 0, 20, 7, 16, 5, 3, 15, 9],             # version A
                                        [12, 1, 0, 5, 15, 16, 3, 17, 15, 21, 13, 12, 14, 13, 27, 30, 33, 2, 2, 27, 29, 10, 22, 37, 2]]  # version B
    """2x25 matrix of page IDs associated to each question of tests A and B for study 4"""
    matTestPageDict = {"MT2":matTestPageStudy23, "MT3":matTestPageStudy23, "MT4":matTestPageStudy4, "MT4.5":matTestPageStudy4}
    """dictionary linking the value of subject.study with the correct test/page matrix for that study"""
    matTestCorrectAnswers = [["C", "C", "B", "B", "C", "C", "D", "D", "A", "C", "B", "D", "A", "A", "C", "D", "B", "A", "A", "D", "A", "B", "B", "D", "C"],    # version A
                                          ["A", "A", "C", "A", "C", "A", "B", "C", "D", "B", "B", "A", "D", "D", "B", "D", "D", "D", "A", "D", "C", "A", "D", "B", "A"]]   # version B
    """2x25 matrix of correct answer ID for the two tests on the circulatory system - should ideally be read from the XML file instead"""
    nonValidTestQuestions = [[8, 10, 12],                  # version A
                                        [2, 12, 13, 15, 20]]       # version B
    """IDs of questions for which post-test score tended to be lower than pre-test (according to a post-analysis) and which should be excluded when calculating scores"""
    possibleSubgoalsNamesID = {"Path of blood flow":1,
                               "Heartbeat":2,
                               "Heart components":3,
                               "Blood vessels":4,
                               "Blood components":5,
                               "Purposes of the circulatory system":6,
                               "Malfunctions of the circulatory system":7}
    """dictionary of possible subgoals names, associating each name to an ID from 1 to 7"""
    possibleSubgoalsIDNames = dict((v, k) for k, v in possibleSubgoalsNamesID.items())
    """dictionary of possible ID for subgoals, associating each of them to a name"""

    nbSubgoalsSetInitially = {"MT2":3, "MT3":3, "MT4":2,"MT4.5":2}
    """number of subgoals set in the initial subgoals setting phase, depending on the study"""
    nbMaxSubgoalsInStudy = {"MT2":7, "MT3":7, "MT4":7, "MT4.5":7}
    """maximum number of subgoals that are available in the study and can be set during the learning session"""

    minNoteTime = datetime.timedelta(seconds=1)
    """minimum time required for a note-taking/note-checking event to be considered as meaningful and counted"""

    def __init__(self, logger, readFiles=True, saveJSONlogInfo=False, doPickle=False, fullBasePathForLogs=".", fileToWrite="subjinfo.txt", subjectsIDToDebug=[], maxFilesToConsider=-1, startTimeStamps=None, stopTimeStamps=None):
        """Creates a MTLogAnalyzer, either from log files or from the dump of a previously created MTLogAnalyzer"""
        self.subjects = []
        """table of subjects"""
        self.fileSubjectsInfo = fileToWrite
        """name of the file where summarized information about subjects will be stored"""
        self.logger = logger
        """logger for system messages"""

        filesLeftToConsider = maxFilesToConsider    # in order to get only some files, mainly for testing purpose when facing an issue with the first file, there is no need to load them all into memory
        allFilesExist = True
        if readFiles:
            # Retrieve information about the subjects from previously existing files
            for suffix in self.dictSubjDataType.values():
                allFilesExist = allFilesExist and (os.path.isfile(self.fileSubjectsInfo.split(".")[0] + suffix[0] + "." + self.fileSubjectsInfo.split(".")[1]))
            if not allFilesExist:
                self.logger.warning("Program has been asked to use already existing data, but some of them were missing - they will need to be analyzed")
            else:
                # Retrieve information from the pickled version (not the CSV files)
                for _, _, filenames in os.walk(fullBasePathForLogs): # + '../data/'):
                    for filename in filenames:
                        if filesLeftToConsider == 0:
                            break
                        if filename.startswith("subject") and filename.endswith(".pkl"):
                            #with open('../data/' + filename, 'rb') as f:
                            with open(fullBasePathForLogs + "\\" + filename, 'rb') as f:
                                self.logger.info("Unpickling from " + filename + "...")
                                self.subjects.append(pickle.load(f))
                                filesLeftToConsider -= 1

        if not readFiles or not allFilesExist:
            # Analyze all the subjects
            self.readSubjectsFiles(fullBasePathForLogs)
            # Parse them to extract custom extended log events
            mtlp = MTLogParser()
            for i, subj in enumerate(self.subjects):
                if filesLeftToConsider == 0:
                    break
                self.logger.info("Parsing MT log for subject " + str(i+1) + " with ID " + str(subj.ID))
                if subjectsIDToDebug != []:
                    if subj.ID in subjectsIDToDebug:    # to parse only a particular list of subjects, for debugging
                        # mtlp.parseDay1LogEvents(self.logger, subj, self.matTestCorrectAnswers)
                        mtlp.parseDay2LogEvents(self.logger, subj, self.matPageSubgoalDict, self.possibleSubgoalsNamesID, stopTimeStamp=stopTimeStamps[subj.ID], startTimeStamp=startTimeStamps[subj.ID]) #Rohit : changed to dictionary for subject specific stop and start times.
                else:
                    # mtlp.parseDay1LogEvents(self.logger, subj, self.matTestCorrectAnswers)
                    mtlp.parseDay2LogEvents(self.logger, subj, self.matPageSubgoalDict, self.possibleSubgoalsNamesID, stopTimeStamp=stopTimeStamps[subj.ID], startTimeStamp=startTimeStamps[subj.ID])#Rohit : changed to dictionary for subject specific stop and start times.
                filesLeftToConsider -= 1

            # Write 5 separate files, for the different kind of data
            for dataType in self.dictSubjDataType.keys():
                self.writeCSVSummary(dataType)
            # Pickle them too, for easy reimport that would otherwise require to reparse the CSV files, making the whole operation quite pointless
            if doPickle:
                # first, delete the already pickled subjects, to avoid keeping some old ones if there used to be more of them
                files = [f for f in os.listdir('./data') if os.path.isfile(f)]
                for filename in files:
                    os.remove('./data/'+filename)
                for i, subject in enumerate(self.subjects):
                    idsubj = ("000" + str(i+1))[-4:]    # get an ID with 4 characters, in order to keep the files in the right order of the subjects (for when they get read)
                    with open('./data/subject' + idsubj + '.pkl', 'wb') as f:
                        self.logger.info("Pickling into subject" + idsubj + ".pkl...")
                        pickle.dump(subject, f)

            if saveJSONlogInfo:
                self.logger.info("Saving participants information into a JSON file...")
                dictJSON = {}
                # save the log location into a JSON file
                for i, subj in enumerate(self.subjects):
                    dictJSON[subj.ID[-5:]] = {"fullId":subj.ID,"logsLocation":{"metaTutor":{"day1":subj.day1File, "day2":subj.day2File}, "faceReader":"", "eyeTracker":""}}

                with open('./data/MetaTutorSubjectsInfo.json', 'w') as f:
                    jsonData = json.dumps(dictJSON, sort_keys=True, indent=4)
                    f.write(jsonData)


    def readSubjectsFiles(self, fullBasePathForLogs):
        """Retrieve all the possible information from the subjects log files, create subsequent MTSubject objects and store them into the self.subjects list"""
        logfilenames = []
        """List of log file names to be read to find subject information"""

        # get the files to be taken into account by the program
        for dirpath, _, filenames in os.walk(fullBasePathForLogs):
            for filename in filenames:
                if filename.endswith(".log"):
                    logfilenames.append(dirpath + "/" + filename)

        print(str(len(logfilenames)) + " - " + str(fullBasePathForLogs))
        if len(logfilenames) == 0:
            self.logger.warning("No logs have been found in the given directory: " + fullBasePathForLogs)
        logfilenames.sort()
        for filename in logfilenames:       # for all the filenames given as parameters to the program
            print("!!!!!!!!!",  filename)
            curSubjectData = []
            curSubjectPage = []
            curSubjectEvents = []
            with open(filename, 'r') as f:
                self.logger.info("Processing subject file: " + filename)
                fcsv = csv.reader(f, delimiter='\t')
                inSessionPart = False       # we start by analyzing the summary part of the log, not the session one
                for i, line in enumerate(fcsv):
                    if (line[0] == "1"):
                        inSessionPart = True    # from now on, every line will be from the session
                        #break               # stop when we have finished reading the header of the logfile

                    if (i == 0):
                        if (line[1] not in self.versionsSupported):
                            self.logger.warning("The log has been generated by a version of MetaTutor that might not be supported - please check carefully the format hasn't changed")
                        else:               # depending on the version, we get the current value for the log level of the summary
                            curSumLogLOD = self.summaryLogLevelOfDetails[self.versionsSupported.index(line[1])] # if before 1.1.21, most info is missing in day 1
                    # Temporarily store the subjectID, subjectName and experimenter
                    elif ((i == 1 and curSumLogLOD<2) or (i == 2 and curSumLogLOD==2)):     # from 1.2.x, an additional line for the screen resolution shifts the line numbers
                        curSubjectID = line[1]
                    elif ((i == 2 and curSumLogLOD<2) or (i == 3 and curSumLogLOD==2)):
                        curSubjectName = line[1]
                    elif ((i == 3 and curSumLogLOD<2) or (i == 4 and curSumLogLOD==2)):
                        curExperimenter = line[1]
                    # Then depending on if it's a Day 1 or Day 2 file
                    elif ((i == 4 and curSumLogLOD<2) or (i == 5 and curSumLogLOD==2)):
                        subjectIdx = self.findSubject(curSubjectID)
                        if len(curSubjectID) < 5:   # don't accept names of less than 5 characters (the regular ID format), while more is generally ok
                            raise Exception("Problem while reading " + filename + ": Subject " + curSubjectID + " has a too short ID number (5 characters normally)")
                        if line[1] == "Presession":   # i.e. Day 1: it's a new subject, add cells to corresponding rows
                            # Day 2 can't have been read already, because of the way filelogs are named based on timestamps
                            # If the subject already exists, there should be a warning
                            if (subjectIdx != -1):
                                raise Exception("Problem while reading " + filename + ": Subject " + curSubjectID + " was already in table")
                            firstSession = True
                        else:                       # i.e. Day 2: find the right row number for the subject
                            if (subjectIdx == -1):
                                raise Exception("Problem while reading " + filename + ": No Day 1 found for the subject " + curSubjectID)
                            curSubjectData.append(line[1])
                            firstSession = False
                    else:
                        if (not inSessionPart):     # other lines from the summary session
                            if (line[0] == "Day"):  # double-check the day number
                                if (firstSession and line[1] != "1") or (not firstSession and line[1] != "2"):
                                    self.logger.warning(filename + " day hasn't been identified properly")
                            else:
                                curSubjectData.append(line[1])  # store them in the general purpose set curSubjectData

                        else:                       # for the actual session content
                            data = self.readPageInfo(line)
                            if data != None:
                                curSubjectPage.append(data)
                            #else:
                            data = self.readLogEvent(line)
                            if data != None:
                                curSubjectEvents.append(data)
                            # TODO: other read*Info functions that would extract data similarly to what readPageInfo does for the Page views

                curSubjectData.append(filename.split("/")[-1])
                if (firstSession):
                    self.subjects.append(MTSubject(self.logger, curSubjectID, curSubjectName, curExperimenter, curSubjectData, curSumLogLOD, curSubjectEvents, self.nbMaxSubgoalsInStudy, self.nbSubgoalsSetInitially))    # add a new subject to the list
                else:
                    offset = 0 if curSumLogLOD<2 else 1
                    self.subjects[subjectIdx].appendDay2Data(self.logger,curSubjectID, curSubjectName, curExperimenter, curSubjectData, curSubjectEvents, offset)   # add information about the day 2 of an existing subject of the list
                    self.subjects[subjectIdx].appendPageData(self.logger,curSubjectPage)                                                                    # add information about the pages visited by a subject

                # """Removed condition for Day 1 to parse 2016 files which have only day 2"""
                # self.subjects.append(MTSubject(self.logger, curSubjectID, curSubjectName, curExperimenter, curSubjectData, curSumLogLOD, curSubjectEvents, self.nbMaxSubgoalsInStudy, self.nbSubgoalsSetInitially))    # add a new subject to the list
                # offset = 0 if curSumLogLOD<2 else 1
                # self.subjects[subjectIdx].appendDay2Data(self.logger,curSubjectID, curSubjectName, curExperimenter, curSubjectData, curSubjectEvents, offset)   # add information about the day 2 of an existing subject of the list
                # self.subjects[subjectIdx].appendPageData(self.logger,curSubjectPage)                                                                    # add information about the pages visited by a subject

    def readLogEvent(self, logline):
        """Return an appropriate event object depending on the content of the log line given as parameter"""
        if logline[3] == "1":
            if logline[4].startswith("Page -"):
                return Browsing.MTBrowsingPageEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
            elif logline[4].startswith("Image View -"):
                return Browsing.MTBrowsingImageEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
            elif logline[4].startswith("Reading Time"):
                return Browsing.MTBrowsingReadingEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
            elif logline[4].startswith("Tutorial"):
                return Browsing.MTBrowsingVideoEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
            elif logline[4] in ["Stop", "Session was normally terminated because of time out."]:
                return Browsing.MTBrowsingSessionEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
            elif logline[4].startswith("Session was restored from unexpected crash."):
                return Browsing.MTBrowsingRestoreAfterCrash(self.logger, logline[0], logline[1], logline[2], logline[4:])
            elif logline[4].startswith("Questionnaire"):
                return Browsing.MTBrowsingQuestionnaire(self.logger, logline[0], logline[1], logline[2], logline[4:])

        elif logline[3] == "2":
            if logline[5] == "AdaptiveRules":
                #return Rule.MTRuleSRLEvent(logline[0], logline[1], logline[2], logline[4:])
                srltype = logline[6].split(']')[0][1:]  # retrieve the SRL type of the event
                # Create the relevant event, depending on the SRL type
                if srltype == "PLAN":
                    return Rule.MTRulePLANEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                elif srltype == "SUMM":
                    return Rule.MTRuleSUMMEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                elif srltype == "TN":
                    return Rule.MTRuleTNEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                elif srltype == "MPTG":
                    return Rule.MTRuleMPTGEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                elif srltype == "RR":
                    return Rule.MTRuleRREvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                elif srltype == "COIS":
                    return Rule.MTRuleCOISEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                elif srltype == "PKA":
                    return Rule.MTRulePKAEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                elif srltype == "JOL":
                    return Rule.MTRuleJOLEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                elif srltype == "FOK":
                    return Rule.MTRuleFOKEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                elif srltype == "CE":
                    return Rule.MTRuleCEEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                elif srltype == "INF":
                    return Rule.MTRuleINFEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                elif srltype == "DEPENDS":
                    return Rule.MTRuleDependsEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                elif srltype == "MEASURE":
                    return Rule.MTRuleMeasureEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
                else:
                    return Rule.MTRuleSRLUnknownEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
            elif logline[5] == "FlowScript":
                if logline[6].startswith("Cannot start"):
                    return Rule.MTRuleFlowCantStart(self.logger, logline[0], logline[1], logline[2], logline[4:])
            elif logline[5] == "MonitoringFlow":
                return Rule.MTRuleQuizEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])

        elif logline[3] == "3":
            if logline[4] == "StudentInput":
                return Dialog.MTDialogUserEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
            elif (logline[4] in ["Gavin", "Mary", "Pam", "Sam"]):
                return Dialog.MTDialogAgentEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
            else:
                raise Exception("Unknown log event: " + str(logline))

        elif logline[3] == "4":
            return Quiz.MTQuizEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])

        elif logline[3] == "5":
            return Notes.MTNoteEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])

        elif logline[3] == "6":
            return Digimemo.MTDigimemoEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])

        elif logline[3] == "7":
            return Layout.MTLayoutEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])

        elif logline[3] == "8":
            if (logline[4] in ["Gavin", "Mary", "Pam", "Sam"]):
                return Agent.MTAgentTalkEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])
            else:
                raise Exception("Unknown log event: " + str(logline))

        elif logline[3] == "9":
            return MetaRule.MTMetaRuleEvent(self.logger, logline[0], logline[1], logline[2], logline[4:])

        return None


    @staticmethod
    def readPageInfo(dataline):
        """Retrieve information from lines related to page views - sends back [PageNumber, timestamp] if the line is page related, None otherwise"""
        if dataline[4].startswith("Page -"):
            #self.lastReadWasRT = False
            # convert the timestamp
            timest = int(dataline[2])
            newtimestamp = (datetime.time(timest // 3600000, (timest // 60000) % 60, (timest // 1000) % 60, (timest % 1000) * 1000)).strftime("%H:%M:%S.%f")[:12]
            #print timest + " ==> " + newtimestamp
            return [dataline[4], newtimestamp]
        else:
            return None

    #def readReadingTimeInfo(dataline):
        #READINGTIME IS NOT REALLY RELEVANT FOR THE VIDEO ANALYSIS, TO RECONSIDER LATER
        #if line[4].startswith("Reading Time"):
        #    if (not self.lastReadWasRT):
        #        curSubjectPage[-1].append(line[5])
        #    else:       # deals with cases where 2 successive reading times are given, in which case we keep only the latest one
        #        curSubjectPage[-1][-1] = line[5]
        #    self.lastReadWasRT = True

    #@staticmethod
    #def addSubjectData(self, idx, colname, val):
    #    """Add a value in the last cell of a row of tabSubjectsInfo, according to the row name"""
    #    if colname in self.subjectsFields:
    #        subjects[idx].
        #for row in tabSubjectsInfo:
        #    if row[0] == colname:
        #        row.append(val)
        #        break

    def findSubject(self, subjectID):
        """Look for a subjectID in the list of subjects"""
        for pos, subject in enumerate(self.subjects):
            if (subject.ID == subjectID or subjectID in subject.ID or subject.ID in subjectID):     # to handle situation where there are extra chars one time only in the ID
                return pos
        return - 1


    ### NOT IN USE ANYMORE ###
#    def getSubjectsInfoString(self, subjectData=False, experimentData=False, pageData=False, eventsData=False, SRLData=False):
#        """Return a chosen set of information about all the subjects as a string with \t between data elements and \n between subjects"""
#        infostring = ""
#        for subject in self.subjects:
#            infostring += subject.getSummaryRowString(logger, subjectData, experimentData, pageData, eventsData, SRLData)
#        return infostring

#    def getSubjectsSetInfoString(self):
#        """Return a predefined set of information about all the subjects as a string"""
#        infostring = ""
#        for subject in self.subjects:
#            infostring += subject.getInfoString()
#        return infostring

#    def getSubjectsSRLString(self, SRLEvent):
#        """Return the information about all the requested SRL events, for all the subjects, as a string"""
#        infostring = ""
#        for subject in self.subjects:
#            infostring += subject.getSRLString(SRLEvent)
#        return infostring

    def printSubjectsUniqueSRL(self, SRLEvent):
        """Print once only each type of information about the requested type of SRL event (and count its number of occurrences), for all the subjects"""
        msglist = []
        msgcountMT2 = []
        msgcountMT3 = []
        for subject in self.subjects:
            for event in subject.day2Events:
                if isinstance(event, SRLEvent):
                    msg = str(event)
                    if msg not in msglist:
                        msglist.append(msg)
                        if subject.study == "MT2":
                            msgcountMT2.append(1)
                            msgcountMT3.append(0)
                        elif subject.study == "MT3":
                            msgcountMT2.append(0)
                            msgcountMT3.append(1)
                    else:
                        if subject.study == "MT2":
                            msgcountMT2[msglist.index(msg)] += 1
                        elif subject.study == "MT3":
                            msgcountMT3[msglist.index(msg)] += 1
        print ("MT2 \tMT3 \t   Event")
        for i, msg in enumerate(msglist):
            print (str(msgcountMT2[i]) + "\t" + str(msgcountMT3[i]) + "\t : " + msg)


    def writeCSVSummary(self, dataType=""): #subjectData=False, experimentData=False, pageData=False, eventsData=False, SRLData=False):
        """Write a chosen set of information about all subjects into a CSV file"""
        if dataType == "" or not dataType in self.dictSubjDataType.keys():
            self.logger.error("A call has been made to writeCSVSummary with an unknown dataType: " + dataType)
            raise Exception("Invalid parameter")

        # Adapts the file name with a suffix telling which data it contains
        filename = self.fileSubjectsInfo.split(".")[0] + self.dictSubjDataType[dataType][0] + "." + self.fileSubjectsInfo.split(".")[1]

        with open(filename, 'wt') as f:
            writer = csv.writer(f, dialect='excel')
            # Write the title of the columns
            #writer.writerow(MTSubject.getSummaryRowTitles(subjectData, experimentData, pageData, eventsData, SRLData))
            coltitles = ["ID", "Group"]
            coltitles.extend(self.dictSubjDataType[dataType][1])
            writer.writerow(coltitles)
            # Write a row per subject
            for subject in self.subjects:
                writer.writerow(subject.getSummaryRowList(self.logger, [dataType], [])) #subjectData, experimentData, pageData, eventsData, SRLData))


    def readCSVSummary(self, dataType=""):
        if dataType == "" or not dataType in self.dictSubjDataType.keys():
            self.logger.error("A call has been made to readCSVSummary with an unknown dataType: " + dataType)
            raise Exception("Invalid parameter")

        pass


    def analyzeNotes(self):
        """Analyze the notes taken by each participant, in order to answer to the following questions:
        1. When were they taken? For how long?
        2. What was the page viewed then? Was it relevant to the subgoal?
        3. What were the events taking place in the 5 minutes before notes were taken?"""
        analysis = ""
        for subject in self.subjects:
            s = ""
            # get all the events looked for, including those before and after
            evtList = subject.getEvents([Custom.CEvtNoteTakeGUI], 2, around=True, typesAround=[Browsing.MTBrowsingEvent], timeBefore=datetime.timedelta(minutes=3), timeAfter=datetime.timedelta(minutes=2))
            # print info about each event from the list
            for event in evtList:
                s += subject.ID + "\t"
                l = map(lambda x: str(x), event.getInfo(showAll=True))
                for i in l:
                    s += i + "\t"
                if isinstance(event, Custom.CEvtNoteTakeGUI):   # for the note-taking events
                    page = subject.getPageInViewWhenEvent(self.logger, event)        # get the page in view
                    s += page + "\t"
                    subgoal = subject.getSubgoalWhenEvent(self.logger, event)        # get the current subgoal
                    if subgoal != 0:
                        try:
                            sgrelevance = self.matPageSubgoalDict[subject.study][subgoal - 1][int(page)]    # get the relevance of the current subgoal
                            #sgrelevance = self.matPageSubgoal[subgoal - 1][int(page)]    # get the relevance of the current subgoal
                        except IndexError:
                            self.logger.error("Unknown page " + page + " or subgoal " + str(subgoal))
                            raise
                        if sgrelevance == 0:
                            s += "irrelevant for SG\t" + self.possibleSubgoalsIDNames[subgoal]
                        elif sgrelevance == 1:
                            s += "relevant for SG\t" + self.possibleSubgoalsIDNames[subgoal]
                        elif sgrelevance == 0.5:
                            s += "partially relevant for SG\t" + self.possibleSubgoalsIDNames[subgoal]
                        else:
                            self.logger.error("Unknown value of relevance: " + str(sgrelevance))
                    else:
                        s += "no SG at this moment"

                s += "\n"
            #print s
            if evtList == []:
                s += subject.ID + "\t" + "No events for this participant\n"
            analysis += s       # Store information about this participant before going to the next one

        return analysis


    def analyzePageViewsAndRelevance(self):
        """Analyze the pages viewed by each participant and add the information about the relevance of the page for the current subgoal of this user"""
        analysis = ""
        for subject in self.subjects:
            self.logger.info("Analyzing pages of subject " + str(subject.ID) + "...")
            s = ""
            # get all the events looked for, including those before and after
            evtList = subject.getEvents([Browsing.MTBrowsingPageEvent], 2, around=False)
            # print info about each event from the list
            for event in evtList:   # for all the page events
                s += subject.ID + "\t"
                l = map(lambda x: str(x), event.getInfo(showAll=True))
                for i in l:
                    s += i + "\t"

                #logger.info("Event page: " + str(event.pageIdx))
                subgoal = subject.getSubgoalWhenEvent(self.logger, event)        # get the current subgoal
                #if subgoal != 0:
                if subgoal > 0:
                    try:
                        sgrelevance = self.matPageSubgoalDict[subject.study][subgoal - 1][int(event.pageIdx)]    # get the relevance of the current subgoal
                        #sgrelevance = self.matPageSubgoal[subgoal - 1][int(event.pageIdx)]    # get the relevance of the current subgoal
                    except IndexError:
                        self.logger.error("Unknown subgoal " + str(subgoal))
                        raise
                    if sgrelevance == 0:
                        s += "irrelevant for SG\t" + self.possibleSubgoalsIDNames[subgoal]
                    elif sgrelevance == 1:
                        s += "relevant for SG\t" + self.possibleSubgoalsIDNames[subgoal]
                    elif sgrelevance == 0.5:
                        s += "partially relevant for SG\t" + self.possibleSubgoalsIDNames[subgoal]
                    else:
                        self.logger.error("Unknown value of relevance: " + str(sgrelevance))
                else:
                    s += "no SG at this moment"

                s += "\n"
            #print s
            if evtList == []:
                s += subject.ID + "\t" + "No events for this participant\n"
            analysis += s       # Store information about this participant before going to the next one

        return analysis


    def analyzeSRLperPage(self):
        """Extract the SRL processes performed while on each page with associated time information
        and return a list of rows (as list) to be printed into a CSV file"""
        res = []    # result list
        for subject in self.subjects:
            self.logger.info("Analyzing pages of subject " + str(subject.ID) + "...")
            #evtList = subject.getEvents([Browsing.MTBrowsingPageEvent, Rule.MTRuleSRLEvent], 2, around=False)   # retrieve page navigation and SRL processes events
            evtTypes = [Browsing.MTBrowsingPageEvent, Custom.CEvtUserTypingSummary, Custom.CEvtUserTypingPKA, Custom.CEvtUserTypingINF,
                            Custom.CEvtNoteTakeGUI, Custom.CEvtNoteCheckGUI, Custom.CEvtUserMovingTowardGoalMPTG,
                            Custom.CEvtUserJudgingLearningJOL, Custom.CEvtUserFeelingKnowledgeFOK, Custom.CEvtUserEvaluatingContentCE,
                            Rule.MTRulePLANEvent, Rule.MTRuleCOISEvent, Rule.MTRuleRREvent, Rule.MTRuleDependsEvent, Rule.MTRuleSRLUnknownEvent]
            evtList = subject.getEvents(evtTypes)
            currentPageIdx = -1
            currentPageTitle = ""
            for evt in evtList: # process all the events
                if isinstance(evt, Browsing.MTBrowsingPageEvent):   # save information relatively to the page currently being viewed
                    currentPageIdx = evt.pageIdx
                    currentPageTitle = evt.pageTitle
                elif isinstance(evt, Rule.MTRuleSRLEvent):    # everytime an SRL action is found, save new line
                    res.append([subject.ID, subject.group, evt.timestamp, "-", "N/A", currentPageIdx, currentPageTitle, evt.SRLType])   # no end time and duration are available for those events
                elif True in [isinstance(evt, evtType) for evtType in evtTypes]:   # custom events which have a MTEvent field
                    if evt.MTEvent == None:   # only the initial PKA and TN events might not have a MTEvent associated
                        if isinstance(evt, Custom.CEvtUserTypingPKA):
                            srlType = "PKA"
                        elif isinstance(evt, Custom.CEvtNoteTakeGUI) or isinstance(evt, Custom.CEvtNoteCheckGUI):
                            srlType = "TN"
                        else:
                            self.logger.warning("Found an unknown SRL advanced event without any associated MTEvent: " + evt)
                            srlType = ""
                    else:
                        srlType = evt.MTEvent.SRLType
                    res.append([subject.ID, subject.group, evt.timeStart, evt.timeEnd, evt.duration, currentPageIdx, currentPageTitle, srlType])
        return res

    def analyzeCOIS(self):
        """Analyze COIS using the eyetracking log analysis"""
        participantsWithValidETList = [#"41004", "41005", "41013", "41015", "41083"    no AOIs in ET log
                                       "41006", "41007", "41008", "41009", "41010", "41011", "41012", "41014", "41016", "41017", "41018", "41019",
                                       "41020", "41022", "41023", "41024", "41027", "41029", "41030", "41032", "41033", "41035", "41036", "41037", "41038", "41039",
                                       "41040", "41041", "41042", "41043", "41044", "41045", "41048", "41049", "41050", "41051", "41052", "41053", "41054", "41055", "41056", "41058", "41059",
                                       "41060", "41061", "41064", "41065", "41066", "41068", "41069", "41070",  "41071", "41072", "41073", "41075", "41076", "41078", "41079",
                                       "41080", "41081", "41082", "41084", "41085", "41086", "41087", "41088", "41089", "41090", "41091", "41092", "44077"]
        pageIdsToConsider = [0, 3, 8, 11, 17, 19, 22]
        periodsOkForCOIS = []


        FixationTime = recordtype("FixationTime", "nbFixations, timeStart, timeEnd, type")
        pageTextAndImageFixations = {}  # double dictionary: first index is the page id, second index the participant id
        for page in pageIdsToConsider:
            pageTextAndImageFixations[page] = {}
            for participant in participantsWithValidETList:
                pageTextAndImageFixations[page][participant] = [False, False]

        for participantID in participantsWithValidETList:
            print ("Participant " + str(participantID) + ":")
            inPageToConsider = False
            inLayoutWithContentVisible = False
            imageVisible = False
            okForCOIS = False
            okTimeStart = None

            aoiFixations = ETLogParser.parseAOILog(participantID)
            print (str(len(aoiFixations)) + " AOIs fixated")
            print (aoiFixations)
            subject = self.subjects[self.findSubject(participantID)]
            evtPageImgList = subject.getEvents([Browsing.MTBrowsingPageEvent, Browsing.MTBrowsingImageEvent, Layout.MTLayoutEvent], 2, around=False)
            #if evt in evtPageImgList:
            for evt in evtPageImgList:
                if isinstance(evt, Browsing.MTBrowsingPageEvent):   # when a new page is opened, check if it's in the valid list
                    currentPageId = int(evt.pageIdx)
                    inPageToConsider = currentPageId in pageIdsToConsider
                    if inPageToConsider:
                        pageTextAndImageFixations[currentPageId][participantID][0] = True # mark the page as visited for that participant
                        #print "visit to valid page"
                    imageVisible = False    # image closed when leaving page
                elif isinstance(evt, Layout.MTLayoutEvent): # when the layout change, check if we are in one of the three that allows to see the page content (Normal, FullView, Notes)
                    inLayoutWithContentVisible = True if evt.layout in ["Normal", "FullView", "Notes"] else False
                elif isinstance(evt, Browsing.MTBrowsingImageEvent):    # when an image is opened
                    imageVisible = True
                    if inPageToConsider:
                        pageTextAndImageFixations[currentPageId][participantID][1] = True # mark the image as opened for that participant
                if inPageToConsider and inLayoutWithContentVisible and imageVisible:    # all conditions are met
                    #print "conditions met"
                    okForCOIS = True
                    okTimeStart = evt.absoluteTime
                    okPageId = currentPageId
                else:
                    if okForCOIS:   # all conditions are not met anymore, but were until now
                        okForCOIS = False
                        okTimeEnd = evt.absoluteTime
                        periodsOkForCOIS.append([okTimeStart, okTimeEnd])
                        print ("start: " + str(okTimeStart) + "\t end: " + str(okTimeEnd))
                        for aoifix in aoiFixations:
                            if (aoifix.timeEnd >= okTimeStart and aoifix.timeStart <= okTimeEnd):
                                # consider this sequence of fixations
                                if "Text" in aoifix.aoiName:
                                    #print "AOI text: " + str(aoifix.aoiName)
                                    pageTextAndImageFixations[okPageId][participantID].append(FixationTime(nbFixations = aoifix.nbFixations, timeStart = aoifix.timeStart, timeEnd = aoifix.timeEnd, type = "text"))
                                elif "Image" in aoifix.aoiName:
                                    #print "AOI image: " + str(aoifix.aoiName)
                                    pageTextAndImageFixations[okPageId][participantID].append(FixationTime(nbFixations = aoifix.nbFixations, timeStart = aoifix.timeStart, timeEnd = aoifix.timeEnd, type = "image"))
            for page in pageIdsToConsider:
                print ("- Page " + str(page) + ":")
                print (pageTextAndImageFixations[page][participantID])

        res = ""
        for page in pageIdsToConsider:
            for participantID in participantsWithValidETList:
                startline = str(participantID) + "\t" + str(page) + "\t" + str(pageTextAndImageFixations[page][participantID][0]) + "\t" + str(pageTextAndImageFixations[page][participantID][1]) + "\t"
                if len(pageTextAndImageFixations[page][participantID]) == 2:
                    res += startline + "\t\t\t\n"
                else:
                    for fix in pageTextAndImageFixations[page][participantID][2:]:
                        res += startline + fix.timeStart.strftime("%H:%M:%S.%f")[:-3] + "\t" + fix.timeEnd.strftime("%H:%M:%S.%f")[:-3] + "\t" + str(fix.nbFixations) + "\t" + fix.type + "\n"
        print(res)
        return res


    def analyzePageInterruptions(self, logger):
        """Check for a list of pages the interruptions user had when viewing them"""
        #pageIdsToConsider = [17, 19]    # 17 and 19 correspond to files 1819 and 2122
        pageIdsToConsider = [0, 2, 3, 5, 15, 16, 30]  # all the pages tested in both versions of the test
        minimumTimeOnPageToConsider = datetime.timedelta(seconds=10) # minimum time in second to be spent on page
        pageInterruptions = {}  # dictionary associating for each participant another dictionary with the number of interruptions in each of the page considered during each visit
        # e.g., "41001":{17:[[AgentInterruption1, AgentInterruption2],[AgentInterruption3]} means participant 41001 has been interrupted twice during their first visit of page 17 and once the second time, and didn't visit other pages considered
        Sequence = recordtype("Sequence", "timeStart, durationOverall, durationWithContent, agentInterruptions")
        AgentInterruption = recordtype("AgentInterruption", "timeStart, timeEnd, agentName, agentScript, layoutChange")
        scoreOnQuestionsToConsider = {} # dictionary associating for each participant another dictionary with the pretest and posttest scores associated to each page to consider

        for subject in self.subjects:
            print("Participant " + str(subject.ID))
            # Calculate the score on the questions relative to the pages to consider for this participant
            scoreOnQuestionsToConsider[subject.ID] = {}
            for page in pageIdsToConsider:  # initialize the score and max score for each relevant page for this participant to 0 for the pretest and posttest
                scoreOnQuestionsToConsider[subject.ID][page] = [[0, 0], [0, 0]] # pretest score, pretest max score, posttest score, posttest max score

            #testQuestionsToConsider = [[self.matTestPageDict[subject.study][i][j] for j in pageIdsToConsider] for i in range(2)] # get questions associated to pages to consider as two sublists (one for test A, one for test B)
            for idxT, test in enumerate(["pre", "post"]):   # for both tests
                print(str(subject.ID) + " " + subject.testsVersion[idxT])
                idxTest = 0 if subject.testsVersion[idxT] == "A" else 1 # index of the questionnaire corresponding to the pre/post-test, depending on the versoin
                for idxQ, pageForQuestion in enumerate(self.matTestPageDict[subject.study][idxTest]):  # get questions associated to considered pages
                    if pageForQuestion in pageIdsToConsider:
                        scoreOnQuestionsToConsider[subject.ID][pageForQuestion][idxT][0] += subject.getScoreOnQuestion(logger, test, idxQ) # add the score to that question
                        scoreOnQuestionsToConsider[subject.ID][pageForQuestion][idxT][1] += 1
                print(scoreOnQuestionsToConsider[subject.ID])

            pageInterruptions[subject.ID] = {}  # initialize the dictionary of interruptions associated to this subject
            onPageToConsider = False
            newSequence = False
            currentPageIdx = -1
            waitingForAgentInterruptingName = False
            waitingForLayoutChangeInfo = False
            waitingForLayoutBackToNormal = False
            changeLayoutRefTimestamp = ""
            evtsList = subject.getEvents([Browsing.MTBrowsingPageEvent, Layout.MTLayoutEvent, Dialog.MTDialogAgentEvent, Rule.MTRuleSRLEvent, Rule.MTRuleMeasureEvent], 2, around=False)

            for evt in evtsList:
                if isinstance(evt, Browsing.MTBrowsingPageEvent):   # check if page is relevant and if so, how many times it has been visited so far
                    waitingForLayoutBackToNormal = False
                    onPageToConsider = False
                    if evt.timeSpentWithContent >= minimumTimeOnPageToConsider:    # do not consider pages that are just reviewed very briefly
                        onPageToConsider = int(evt.pageIdx) in pageIdsToConsider
                        currentPageIdx = int(evt.pageIdx)
                        if onPageToConsider:    # count the number of visits on considered pages
                            print("Visit to page " + str(currentPageIdx))
                            newSequence = True
                            sequence = Sequence(durationOverall = evt.timeSpentOverall, durationWithContent = evt.timeSpentWithContent, timeStart = evt.timestamp, agentInterruptions = [])  # save the time spent on that page
                            if currentPageIdx in pageInterruptions[subject.ID]: # if there have already been pages interruptions recorded for the current page
                                pageInterruptions[subject.ID][currentPageIdx].append(sequence)    # new visit to a page already visited
                            else:
                                pageInterruptions[subject.ID][currentPageIdx] = [sequence]    # visit to previously unvisited page
                elif isinstance(evt, Dialog.MTDialogAgentEvent) and onPageToConsider and waitingForAgentInterruptingName:   # Agent talked while on a page considered (interruption)
                    waitingForAgentInterruptingName = False
                    pageInterruptions[subject.ID][currentPageIdx][-1].agentInterruptions[-1].agentName = evt.agentName
#                    print "Agent talk"
#                    interruption = AgentInterruption(agentName = evt.agentName, agentScript = evt.scriptID, layoutChange = False)
#                    if not newSequence: # if there have already been page interruptions recorded for the current page in the current visit to the page
#                        pageInterruptions[subject.ID][currentPageIdx][-1].append(interruption)  # add an interruption to the last sequence
#                    else:   # first interruption recorded in this sequence of visit
#                        pageInterruptions[subject.ID][currentPageIdx][-1] = [interruption]  # create a new list of interruptions with the current sequence
#                        newSequence = False
                elif isinstance(evt, Layout.MTLayoutEvent) and onPageToConsider and (waitingForLayoutChangeInfo or waitingForLayoutBackToNormal): # Layout changed while on a page considered (interruption with layout change)
                    print("Layout change")
                    if waitingForLayoutChangeInfo:
                        waitingForLayoutChangeInfo = False
                        # since normally the agent always talks before the layout changes, there is already an AgentInterruption existing
                        pageInterruptions[subject.ID][currentPageIdx][-1].agentInterruptions[-1].layoutChange = True   # change the layoutChange attribute of the last (ongoing) interruption of the last sequence
                    if waitingForLayoutBackToNormal and evt.layout in ["Normal", "FullView", "Notes"] and ((evt.timestamp - changeLayoutRefTimestamp) > datetime.timedelta(seconds=1)):   # the layout goes back to normal, end of the interruption (ignore if in the same second as when the interruption started, as sometimes it goes back to Normal briefly)
                        waitingForLayoutBackToNormal = False
                        pageInterruptions[subject.ID][currentPageIdx][-1].agentInterruptions[-1].timeEnd = evt.timestamp
                elif isinstance(evt, Rule.MTRuleEvent) and onPageToConsider:
                    realInterruption = False
                    if isinstance(evt, Rule.MTRuleSRLEvent):
                        if evt.initiative == "agent":
                            realInterruption = True
                            waitingForAgentInterruptingName = True
                            interruption = AgentInterruption(timeStart = evt.timestamp, timeEnd = "TBD", agentName = "TBD", agentScript = evt.SRLType, layoutChange = False)
                    elif isinstance(evt, Rule.MTRuleMeasureEvent):
                        if evt.questionnaireName != "SEIAloneStart":    # as this happens when user changed subgoal while on page, and is therefore not an interruption
                            realInterruption = True
                            interruption = AgentInterruption(timeStart = evt.timestamp, timeEnd = "TBD", agentName = "Gavin", agentScript = evt.questionnaireName, layoutChange = True)
                    if realInterruption:
                        print("Rule triggered on page " + str(currentPageIdx))
                        waitingForLayoutChangeInfo = True
                        waitingForLayoutBackToNormal = True
                        changeLayoutRefTimestamp = evt.timestamp    # save this timestamp in order to discard changing layout in the same second
               #         if not newSequence: # if there have already been page interruptions recorded for the current page in the current visit to the page
                        pageInterruptions[subject.ID][currentPageIdx][-1].agentInterruptions.append(interruption)  # add an interruption to the last sequence
                #        else:   # first interruption recorded in this sequence of visit
                #        pageInterruptions[subject.ID][currentPageIdx][-1].agentInterruptions = [interruption]  # create a new list of interruptions with the current sequence
                #            newSequence = False
                if isinstance(evt, Rule.MTRulePLANEvent):
                    if (evt.startingAction == "PostTestIntro" and waitingForLayoutBackToNormal):        # if the end of the session comes, there is no come back to a Normal layout, so it needs to be treated as a special case
                        waitingForLayoutBackToNormal = False
                        pageInterruptions[subject.ID][currentPageIdx][-1].agentInterruptions[-1].timeEnd = evt.timestamp
            print(pageInterruptions[subject.ID])

        res = "Participant ID\tPage ID\tPage PreTest score\tPage PreTest max score\tPage PostTest score\tPage PostTest max score\tPage opened\t# Sequence\tTotal # of sequences\tSequence start time\tSequence duration overall (s)\tSequence duration with content (s)\t# Interruption\tTotal # of interruptions (in sequence)\tInterruption start (s - relative to sequence start time)\tInterruption duration (s)\tAgent\tEvent\tLayout Change\n"
        for subject in pageInterruptions.keys():
            for page in pageIdsToConsider:
                startline = subject + "\t" + str(page) + "\t" + str(scoreOnQuestionsToConsider[subject][page][0][0]) + "\t" + str(scoreOnQuestionsToConsider[subject][page][0][1]) + "\t" + str(scoreOnQuestionsToConsider[subject][page][1][0]) + "\t" + str(scoreOnQuestionsToConsider[subject][page][1][1]) + "\t"
                if not page in pageInterruptions[subject]:   # the subject didn't visit that page
                    res += startline + "no" + "\t\t\t\t\t\t\t\t\t\t\t\t\n"
                else:
                    for idxSeq, sequence in enumerate(pageInterruptions[subject][page]):
                        if len(sequence.agentInterruptions) == 0:   # if the page has been visited but without any interruption
                            res += startline + "yes\t" + str(idxSeq+1) + "\t"  + str(len(pageInterruptions[subject][page])) + "\t" + str(sequence.timeStart) + "\t" + str(sequence.durationOverall.seconds) + "\t" + str(sequence.durationWithContent.seconds) + "\t\t\t\t\t\t\n"
                        else:
                            for idxInt, interruption in enumerate(sequence.agentInterruptions):
                                res += startline + "yes\t" + str(idxSeq+1) + "\t"  + str(len(pageInterruptions[subject][page])) + "\t"+ str(sequence.timeStart) + "\t" + str(sequence.durationOverall.seconds) + "\t" + str(sequence.durationWithContent.seconds) + "\t" +  str(idxInt+1) + "\t" + str(len(sequence.agentInterruptions)) + "\t"  + str((interruption.timeStart - sequence.timeStart).seconds) + "\t"
                                if interruption.timeEnd != "TBD":
                                    res += str((interruption.timeEnd - interruption.timeStart).seconds)
                                else:
                                    res += "N/A"
                                res += "\t" + interruption.agentName + "\t" + interruption.agentScript + "\t" + str(interruption.layoutChange) + "\n"
        return res


    def analyzeEV(self, evInfoFile):
        """Cross-reference information about EV quiz with (manually filtered) collected information in the Google Docs questionnaire"""
        with open(evInfoFile, 'r') as fevIn:
            evCsvReader = csv.reader(fevIn, delimiter=",")
            evCsvReader.next()  # skip the title line
            subjectIdx = -1
            qEvIdx = -1
            subjectIdxDict = {}
            for row in evCsvReader:
                # check if we have changed subject from previous row: if not, increment the questionnaire number to be retrieved
                if self.findSubject(row[1][-5:]) != subjectIdx:
                    subjectIdx = self.findSubject(row[1][-5:])
                    if subjectIdx in subjectIdxDict:
                        subjectIdxDict[subjectIdx] += 1
                    else:
                        subjectIdxDict[subjectIdx] = 0
                else:
                    subjectIdxDict[subjectIdx] += 1
                qEvIdx = subjectIdxDict[subjectIdx]


                # retrieve the proper questionnaire for this subject, and associate the values provided as replies to the questionnaire
                #evQList = self.subjects[subjectIdx].getEventListAsList([[Browsing.MTBrowsingQuestionnaire, {"showAll":True}]])
                #evQEVList = []
                #for questionnaire in evQList:
                #    if questionnaire.questionnaireName == "EIV":
                #        evQEVList.append(questionnaire)
                evQList = self.subjects[subjectIdx].getEvents([Questionnaire.MTQuestionnaireEIV], 2)
                evQList[qEvIdx].setQuestionnaireReplies(row[2:])


    def analyzeMetaRules(self, nbMinutesInterval, groups):
        rulesGroups = [["FOKCEChangeRelPageShortTime", "JOLChangeRelPageMediumTime", "MPTGPercentComplete", "PKAEnterPage", "CERelPage", "CEIrrelPage", "JOLRelPageLongTime", "FOKRelPageMediumTime", "MPTGTimeLimit"],
                            ["SUMMChangeRelPageLongTime", "SUMMImgNotOpen", "SUMMImgOpen", "COISRelPageImgNotOpen", "RRRelPageImgOpen", "DRAWRelImgNotOpen", "DRAWRelImgOpen"]]
        rulesGroupsNames = ["Monitoring", "Strategy"]
        rulesGroupsRepresentants = [group[0] for group in rulesGroups]
        TimePct = recordtype("TimePct", "time, monitoring, strategy")
        PctsRep = recordtype("PctsRep", "user, agent")


        pctActive = {}  # work in the referential of the learning session time (not the MetaTutor whole session referential)
        for subject in self.subjects:   # for each subject, retrieve all the metarules event
            pctActive[subject.ID] = [TimePct(time = datetime.datetime(1900, 1, 1, 0, 0, 0, 0) - datetime.datetime(1900, 1, 1, 0, 0, 0, 0), monitoring = PctsRep(50, 50), strategy = PctsRep(50, 50))]  # add an initial object where every pct is at the max value
            evtsList = subject.getEvents([MetaRule.MTMetaRuleEvent], 2, around=False)
            for evt in evtsList:    # keep only one element representative of each category of metarules
                if evt.ruleName in rulesGroupsRepresentants:
                    currentGroup = rulesGroupsNames[rulesGroupsRepresentants.index(evt.ruleName)]
                    # depending on whether it's the monitoring or strategy and agent or system value that changed, create a new object with this timestamp with the 3 previous % and the new updated %
                    if currentGroup == "Monitoring":
                        if evt.initiative == "user":
                            pctActive[subject.ID].append(TimePct(time = evt.timestamp - subject.learningSessionStartTime,
                                                                 monitoring = PctsRep(user = evt.newValue, agent = pctActive[subject.ID][-1].monitoring.agent),
                                                                 strategy = PctsRep(user = pctActive[subject.ID][-1].strategy.user, agent = pctActive[subject.ID][-1].strategy.agent)))
                        else:
                            pctActive[subject.ID].append(TimePct(time = evt.timestamp - subject.learningSessionStartTime,
                                                                 monitoring = PctsRep(user = pctActive[subject.ID][-1].monitoring.user, agent = evt.newValue),
                                                                 strategy = PctsRep(user = pctActive[subject.ID][-1].strategy.user, agent = pctActive[subject.ID][-1].strategy.agent)))
                    elif currentGroup == "Strategy":
                        if evt.initiative == "user":
                            pctActive[subject.ID].append(TimePct(time = evt.timestamp - subject.learningSessionStartTime,
                                                                 monitoring = PctsRep(user = pctActive[subject.ID][-1].monitoring.user, agent = pctActive[subject.ID][-1].monitoring.agent),
                                                                 strategy = PctsRep(user = evt.newValue, agent = pctActive[subject.ID][-1].strategy.agent)))
                        else:
                            pctActive[subject.ID].append(TimePct(time = evt.timestamp - subject.learningSessionStartTime,
                                                                 monitoring = PctsRep(user = pctActive[subject.ID][-1].monitoring.user, agent = pctActive[subject.ID][-1].monitoring.agent),
                                                                 strategy = PctsRep(user = pctActive[subject.ID][-1].strategy.user, agent = evt.newValue)))
                    else:
                        self.logger.warning("Unknown group name: " + str(currentGroup))
        print(pctActive)

        # Now it is possible to extract the mean/std. dev. number of pct changes per period of N minutes
        #tim = [TimePct(time = datetime.datetime(1900, 1, 1, 0, 0, 0, 0), monitoring = [PctsRep(50, 50)], strategy = [PctsRep(50, 50)])]
        pctActivePerPeriod = {}
        nbMinutesInterval = 5
        for subjectId in pctActive:
            pctActivePerPeriod[subjectId] = [TimePct(time = datetime.datetime(1900, 1, 1, 0, 0, 0, 0) - datetime.datetime(1900, 1, 1, 0, 0, 0, 0), monitoring = PctsRep(user = 50, agent = 50), strategy = PctsRep(user = 50, agent = 50))]
            for im, minutes in enumerate(range(nbMinutesInterval, 120, nbMinutesInterval)):
                if im == 0:
                    lastChangeInPeriod = TimePct(time = datetime.datetime(1900, 1, 1, 0, 0, 0, 0) - datetime.datetime(1900, 1, 1, 0, 0, 0, 0), monitoring = PctsRep(user = 50, agent = 50), strategy = PctsRep(user = 50, agent = 50))
                else:
                    lastChangeInPeriod = pctActivePerPeriod[subjectId][-1]  # keep the last value in memory
            #tim.append(TimePct(time = datetime.datetime(1900, 1, 1, 0, minutes, 0, 0), monitoring = [], strategy = []))
                for tpct in pctActive[subjectId]:
                    if tpct.time > (datetime.datetime(1900, 1, 1, (minutes-nbMinutesInterval)/60, (minutes-nbMinutesInterval)%60, 0, 0) - datetime.datetime(1900, 1, 1, 0, 0, 0, 0)) and tpct.time <= (datetime.datetime(1900, 1, 1, minutes/60, minutes%60, 0, 0) - datetime.datetime(1900, 1, 1, 0, 0, 0, 0)):
                        lastChangeInPeriod = tpct
                # make a copy of the last appropriate change in the period of time considered
                lastChangeInPeriod = TimePct(time = datetime.datetime(1900, 1, 1, minutes/60, minutes%60, 0, 0) - datetime.datetime(1900, 1, 1, 0, 0, 0, 0) ,
                                             monitoring = PctsRep(user = lastChangeInPeriod.monitoring.user, agent = lastChangeInPeriod.monitoring.agent),
                                             strategy = PctsRep(user = lastChangeInPeriod.strategy.user, agent = lastChangeInPeriod.strategy.agent))
                pctActivePerPeriod[subjectId].append(lastChangeInPeriod)
        print(pctActivePerPeriod)

        # format the output
        res = [[], [], [], [], [], []]
        variableShown = ["%MonAg", "%MonUs", "%MonAll", "%StrAg", "%StrUs", "%StrAll"]
        for i in range(6):
            headings0 = [variableShown[i]]
            headings1 = ["Condition"]
            headings2 = ["Subject"]
            #headings3 = ["Time"]
            nbColPerSubject = 1
            for nbInt, timeInterval in enumerate(range(len(range(nbMinutesInterval, 120, nbMinutesInterval)))):
                res[i].append([])
                firstSubjectInIntervalFound = False
                for group in groups:
                    for subject in self.subjects:
                        if subject.group == group:
                            if nbInt == 0:  # save the condition and subject names to add on the first line of the output
                                headings0.extend([""] * nbColPerSubject)
                                headings1.extend([subject.group] * nbColPerSubject)
                                headings2.extend([subject.ID] * nbColPerSubject)
                                #headings3.extend(["%MonAg", "%MonUs", "%MonAll", "%StrAg", "%StrUs", "%StrAll"])
                            if not firstSubjectInIntervalFound:
                                firstSubjectInIntervalFound = True
                                res[i][-1].append(pctActivePerPeriod[subject.ID][timeInterval].time)
                            if i == 0:
                                res[i][-1].append(pctActivePerPeriod[subject.ID][timeInterval].monitoring.agent)
                            elif i == 1:
                                res[i][-1].append(pctActivePerPeriod[subject.ID][timeInterval].monitoring.user)
                            elif i == 2:
                                res[i][-1].append(pctActivePerPeriod[subject.ID][timeInterval].monitoring.agent + pctActivePerPeriod[subject.ID][timeInterval].monitoring.user)
                            elif i == 3:
                                res[i][-1].append(pctActivePerPeriod[subject.ID][timeInterval].strategy.agent)
                            elif i == 4:
                                res[i][-1].append(pctActivePerPeriod[subject.ID][timeInterval].strategy.user)
                            elif i == 5:
                                res[i][-1].append(pctActivePerPeriod[subject.ID][timeInterval].strategy.agent + pctActivePerPeriod[subject.ID][timeInterval].strategy.user)
                # add the headings
            res[i].reverse()
            [res[i].append(_) for _ in [headings2, headings1, headings0]]
            res[i].reverse()
        return [item for sublist in res for item in sublist]    # flatten the list of one level

    def getInitialSubgoalSettingSequence(self):
        """Get a list of the interactions between user and agent during the initial subgoal setting phase, for CoRL study"""
        results = []
        subgoalAboutToBeSet = False
        for subject in self.subjects:
            self.logger.info("Analyzing subgoal session of subject " + str(subject.ID) + " (study " + subject.study + ")")
            inSGSession = False
            doneWithThisSubject = False
            sgcpt = 1
            cyccpt = 0
            if (subject.study not in ["MT2", "MT3", "MT4", "MT4.5"]):
                self.logger.warning("Subject " + str(subject.ID) + " will not be printed as they seem to be part of a study not taken into consideration in printInitialSubgoalSettingSequence()" )
            evtList = subject.getEvents([Dialog.MTDialogEvent, Agent.MTAgentTalkEvent, Custom.CEvtSubgoalSet], 2, around=False)
            for evt in evtList:
                # look for the start event
                if (isinstance(evt, Dialog.MTDialogAgentEvent)):
                    if (((subject.study == "MT2" or subject.study == "MT3") and evt.scriptID == "PamSubgoalStart") or ((subject.study == "MT4" or subject.study == "MT4.5") and evt.scriptID == "PamSubgoalStart4")):
                        inSGSession = True
                        self.logger.info("Start session")

#                # check if the end event has been reached
#                if (inSGSession):
#                    if (isinstance(evt, Dialog.MTDialogAgentEvent)):
#                        if (evt.scriptID == "PamSubgoalFinished"):  # stop considering the events when Pam says subgoals phase is over
#                            inSGSession = False      # necessary not to detect subgoals set after the initial phase
#                            print "End session"

                # print event if necessary
                if (inSGSession and not doneWithThisSubject):
                    if (isinstance(evt, Custom.CEvtSubgoalSet)):  # we know the next user answer will be yes, thus ending the current subgoal
                        subgoalAboutToBeSet = True
                    elif (isinstance(evt, Dialog.MTDialogAgentEvent)):
                        if (evt.scriptID == "PamSubgoalFinished"):  # stop considering the events when Pam says subgoals phase is over
                            inSGSession = False      # necessary not to detect subgoals set after the initial phase
                            doneWithThisSubject = True
                            #print "End session"
                        elif (evt.scriptID == "PamSubgoalSelected"):
                            cyccpt = 1
                            sgcpt += 1
                            self.logger.info("SG selected")
                        else:
                            cyccpt += 1
                            self.logger.info("Next cycle")
                    elif (isinstance(evt, Agent.MTAgentTalkEvent)):   # use MTAgentTalkEvent instead of MTDialogAgentEvent because subgoal names aren't replaced otherwise
                        if (evt.type == "Start"):
                            results.append([subject.ID, subject.group, str(sgcpt), str(cyccpt), "[SG" + str(sgcpt) + "C" + str(cyccpt) + "]", evt.scriptID, "Pam", evt.text])
                            self.logger.info("Pam talk")
                    elif (isinstance(evt, Dialog.MTDialogUserEvent)):
                        results.append([subject.ID, subject.group, str(sgcpt), str(cyccpt), "[SG" + str(sgcpt) + "C" + str(cyccpt) + "]", "", "User", evt.input])
                        self.logger.info("User talk")
                        if subgoalAboutToBeSet:
                            subgoalAboutToBeSet = False
        return results


    def getEventListSequenceForDataMining(self, QuizSeparateNAndP=False, mergeActionsInASingleString=True, sample="",
                                          mergeSequenceOfSameActionAsMult=None, groupAllSRLProcesses=True,
                                          separateMonitoringProcessAccordingToRelevanceEstimation=False, separateReadAccordingToRelevance=True, separateReadAccordingToDuration=True, readLongShortThreshold=20,
                                          separateProcessAccordingToEmotionValence=False, timeToConsiderForEmotionAfterProcessStart=10):
        """Return a list of strings corresponding to some events, in order to be used by the HMM Program from Vanderbilt
        @param self the object pointer
        @param QuizSeparateNAndP boolean to define if two distinct actions should be created for quizzes with a positive or negative reply
        @param mergeActionsInASingleString boolean value to export the sequence of action as a single cell separated by ; in the CSV file generated at the end (for the new version of Vanderbilt software package) or if there should be one cell per action (for the old version)
        @param mergeSequenceOfSameActionAsMult boolean to determine if there is a sequence of several identical actions coming one after another (e.g. ReadS, ReadS, ...), they should be replaced by a single action suffixed by MULT (e.g. ReadS-MULT)
        @param groupAllSRLProcesses boolean to specify if SRL processes should be considered as one type of action (SRLa or SRLu) or if we want to split Monitoring (MonA and MonU) from Strategizing (StrA and StrU)
        @param separateMonitoringProcessAccordingToRelevanceEstimation boolean indicating if monitoring processes should be separated according to the relevance user estimation for CE, JOL and FOK
        @param separateReadAccordingToRelevance boolean indicating if reading actions should be distinguished between relevant (ReadR) or irrelevant (ReadI) pages - Read0 when relevance can't be known because no subgoals are set
        @param separateReadAccordingToDuration boolean indicating if reading actions should be distinguished between page visited for a long time (ReadL) or only shortly (ReadS)
        @param readLongShortThreshold integer indicating the number of seconds marking the difference between a short and long visit to a page
        @param separateProcessAccordingToEmotionValence boolean indicating if SRL processes should be separated according to the valence of the emotion felt while performing them
        @param timeToConsiderForEmotionAfterProcessStart integer indicating the number of seconds to check for the dominant valence calculation
        """
        SRLprocU = [
                   [Custom.CEvtUserEvaluatingContentCE, {"showInitiative":True, "showRealRelevancy":True, "showEvaluatedRelevance":True}],
                   [Custom.CEvtUserMovingTowardGoalMPTG, {"showInitiative":True}],
                   [Custom.CEvtUserJudgingLearningJOL, {"showInitiative":True, "showUnderstandingLevel":True}],
                   [Custom.CEvtUserFeelingKnowledgeFOK, {"showInitiative":True, "showKnowledgeLevel":True}],
                   [Rule.MTRuleDependsEvent, {"showRealSRLType":True}],
                   [Rule.MTRuleSUMMEvent, {"showInitiative":True}],
                   [Rule.MTRuleCOISEvent, {"showInitiative":True}],
                   [Rule.MTRuleINFEvent, {"showInitiative":True}],
                   [Rule.MTRuleRREvent, {"showInitiative":True}],
                   [Custom.CEvtSubgoalSuggested, {}],
                   [Custom.CEvtSubgoalSetting, {}],
                   [Custom.CEvtPostponingSubgoal, {}],
                   [Custom.CEvtNoteTakeGUI, {}],
                   [Custom.CEvtNoteCheckGUI, {}],
                   [Custom.CEvtNoteTakenOnPaper, {}],
                   [Custom.CEvtUserTakingQuiz, {"showScore":True, "showScoreMax":True}],
                   [Browsing.MTBrowsingPageEvent, {"showPageIdx":True, "showTimeSpentWithContent":True, "showRelevanceToSubgoal":True}],
                   [Custom.CEvtPursuingNewSubgoal, {"showCurrentSubgoalID":True}]
                   ]
        # TODO: make it easier by using the events themselves, instead of a list of strings, with the following function:
        #evtList = self.getEvents(types, day)

        if type(mergeSequenceOfSameActionAsMult) != bool:
            self.logger.error("The parameter mergeSequenceOfSameActionAsMult must be a boolean value")
            return

        #--- STEP 1: Determine the subject samples to use
        allSamplesID = [
                            [["23028", "23009", "23023", "33041", "23079", "23032", "23034", "23071", "23041", "33011", "33017", "PN33055"], "goodLearners"],
                            [["23045", "23047", "23052", "23067", "33012", "33039", "23050", "MT21PN33054", "23012", "23059", "23018", "23076", "23062"], "badLearners"],
                            [["23012", "23018", "23020", "23028", "23034", "23045", "23047", "23050", "23067", "23070", "23071", "23079", "33007", "33011", "33018", "33038", "33039", "33041", "MT21PN33042", "33052", "34112"], "cluster0M"],
                            [["23005", "23009", "23023", "23027", "23032", "23041", "23059", "23062", "23076", "23080", "34073", "34079", "34091"], "cluster1L"], #34105 originally there (in EDM 2012 paper) but excluded because of problem with MetaTutor
                            [["23003", "23013", "23052", "23057", "33001", "33005", "33009", "33012", "33017", "33031", "33040", "33047", "33050", "MT21PN33053", "33056", "33057"], "cluster2H"]
                     ]
        samplesID = []
        if sample == "good&badLearners":
            samplesID = [allSamplesID[0], allSamplesID[1]]
        elif sample == "3clusters":
            samplesID = [allSamplesID[2], allSamplesID[3], allSamplesID[4]]
        elif sample == "cluster1LvsOthers":
            mergedSamples = allSamplesID[2][0][:]                      # get copy of participants ID from cluster 0
            mergedSamples.extend(allSamplesID[4][0])                # add ID from participants in cluster 2
            mergedSamples = [mergedSamples, "clusters0M2H"]    # add sample name
            samplesID = [allSamplesID[3], mergedSamples]            # samples considered is 1 + the merge
        elif sample == "cluster2HvsOthers":
            mergedSamples = allSamplesID[2][0][:]                      # get copy of participants ID from cluster 0
            mergedSamples.extend(allSamplesID[3][0])                # add ID from participants in cluster 1
            mergedSamples = [mergedSamples, "clusters0M1L"]    # add sample name
            samplesID = [allSamplesID[4], mergedSamples]            # samples considered is 2 + the merge
        elif sample == "":
            self.logger.error("A sample name must be given as a parameter")
            return
        else:
            self.logger.error("Unknown sample name: " + sample)
            return

        print("SAMPLES: " + str(samplesID))

        allRawEvents = []
        """relevant events extracted for the samples considered"""
        for group in samplesID:
            allRawEvents.append([])

        #--- STEP 2: Extract the relevant events from the subjects to be considered
        cptSubjInGroup = []
        IDsTreated = []
        for isubj, subj in enumerate(self.subjects):
            for igroup, group in enumerate(samplesID):
                if isubj == 0:  # initialize the counter for each group
                    cptSubjInGroup.append(0)
                if subj.ID in group[0]:
                    self.logger.info("Treating subject " + str(subj.ID) + "...")
                    allRawEvents[igroup].append([subj.ID])
                    allRawEvents[igroup][-1].append(subj.getEvents(map(lambda _:_[0], SRLprocU), 2, False))
                    cptSubjInGroup[igroup] += 1
                    IDsTreated.append(subj.ID)
        for icpt, cpt in enumerate(cptSubjInGroup): # check that everyone has been found
            if cpt != len(samplesID[icpt][0]):
                self.logger.warning("Only " + str(cpt) + " subjects treated for group " + samplesID[icpt][1] + " instead of " + str(len(samplesID[icpt][0])))
                IDsMissing = ""
                for subj in samplesID[icpt][0]:
                    if subj not in IDsTreated:
                        IDsMissing += str(subj) + " "
                self.logger.warning("Missing IDs: " + IDsMissing)
        print(allRawEvents)

        #--- STEP 3: Group the events with an associated code
        dictAct = {"Notes":0}

        suffixesReadRel = ["R", "I", "0"] if separateReadAccordingToRelevance else [""]
        suffixesReadDur = ["S", "L"] if separateReadAccordingToDuration else [""]
        for suffDur in suffixesReadDur:
            for suffRel in suffixesReadRel:
                dictAct["Read"+suffDur+suffRel] = 0
        if groupAllSRLProcesses:
            monitoringProcessFromUserCat = "SRLu"
            monitoringProcessFromAgentCat = "SRLa"
            strategyProcessFromUserCat = "SRLu"
            strategyProcessFromAgentCat = "SRLa"
        else:
            monitoringProcessFromUserCat = "MonU"
            monitoringProcessFromAgentCat = "MonA"
            strategyProcessFromUserCat = "StrU"
            strategyProcessFromAgentCat = "StrA"
        SRLact = list(set([monitoringProcessFromUserCat, monitoringProcessFromAgentCat, strategyProcessFromUserCat, strategyProcessFromAgentCat]))
        if separateMonitoringProcessAccordingToRelevanceEstimation:
            suffixes=["+", "-", ""]
        else:
            suffixes=[""]
        # add relevant actions to the dictionary, for the SRL processes (Str[U|A][+|-] don't exist though, but it doesn't bother to have them in the dictionary)
        for act in SRLact:
            for suffix in suffixes:
                dictAct[act+suffix] = 0
        if QuizSeparateNAndP:
            dictAct["QuizP"] = 0
            dictAct["QuizN"] = 0
        else:
            dictAct["Quiz"] = 0

        #--- STEP 4: Analyze each subject in each group and generate both a dictionary to count the number of each type of events and a list per subject of the sequences
        for igroup, group in enumerate(allRawEvents):
            # index of the set analyzed, only used to generate different file names
            eventCodeSequences = {} # dictionary of sequences of encoded events associated to the ID of each subject
            for subj in group:  # get the events associated to each subject
                pendingCategory = ""
                currentSG = ""
                pageRelevant = None
                pageRelevancyRelevant = None
                subjID = subj[0]
                eventCodeSequences[subjID] = []    # initialize the list of events associated to this subject (which ID is in position 0)
                for evt in subj[1]:
                    if True in [isinstance(evt, evtType) for evtType in [Rule.MTRuleSUMMEvent, Rule.MTRuleCOISEvent, Rule.MTRuleINFEvent, Rule.MTRuleRREvent]]:
                        if evt.initiative == "user":
                            eventCodeSequences[subjID].append(strategyProcessFromUserCat)
                            dictAct[strategyProcessFromUserCat] += 1
                        elif evt.initiative == "agent":
                            eventCodeSequences[subjID].append(strategyProcessFromAgentCat)
                            dictAct[strategyProcessFromAgentCat] += 1
                        else:
                            self.logger.warning("Unknown initiative for " + str(evt) + ": " + str(evt.initiative))

                    elif True in [isinstance(evt, evtType) for evtType in [Custom.CEvtNoteTakeGUI, Custom.CEvtNoteCheckGUI, Custom.CEvtNoteTakenOnPaper]]:
                        eventCodeSequences[subjID].append("Notes")
                        dictAct["Notes"] += 1

                    elif isinstance(evt, Custom.CEvtSubgoalSuggested):
                        eventCodeSequences[subjID].append(monitoringProcessFromAgentCat)
                        dictAct[monitoringProcessFromAgentCat] += 1

                    elif True in [isinstance(evt, evtType) for evtType in [Custom.CEvtSubgoalSetting, Custom.CEvtPostponingSubgoal]]:
                        eventCodeSequences[subjID].append(monitoringProcessFromUserCat)
                        dictAct[monitoringProcessFromUserCat] += 1

                    elif isinstance(evt, Custom.CEvtUserMovingTowardGoalMPTG):
                        if evt.MTEvent.initiative == "user":
                            eventCodeSequences[subjID].append(monitoringProcessFromUserCat)
                            dictAct[monitoringProcessFromUserCat] += 1
                        elif evt.MTEvent.initiative == "agent":
                            eventCodeSequences[subjID].append(monitoringProcessFromAgentCat)
                            dictAct[monitoringProcessFromAgentCat] += 1
                        else:
                            self.logger.warning("Unknown initiative for " + str(evt) + ": " + str(evt.initiative))

                    elif isinstance(evt, Rule.MTRuleDependsEvent):
                        # initiative always comes from the agent
                        if "CE" in evt.realSRLType: # CE, agent-initiative and with a negative evaluation
                            if separateMonitoringProcessAccordingToRelevanceEstimation and pageRelevancyRelevant:
                                if pageRelevant: # the page is actually relevant, so the user is wrong in their evaluation
                                    eventCodeSequences[subjID].append(monitoringProcessFromAgentCat + "-")
                                    dictAct[monitoringProcessFromAgentCat + "-"] += 1
                                else:   # the page is indeed not relevant, so the user is right in their evaluation
                                    eventCodeSequences[subjID].append(monitoringProcessFromAgentCat + "+")
                                    dictAct[monitoringProcessFromAgentCat + "+"] += 1
                            else:   # we don't take into account the relevance of estimation or no subgoal currently exists (this shouldn't happen though, as then no prompt should come)
                                eventCodeSequences[subjID].append(monitoringProcessFromAgentCat)
                                dictAct[monitoringProcessFromAgentCat] += 1
                        elif "FOK" in evt.realSRLType:  # FOK, agent-initiative and with a positive estimation
                            if separateMonitoringProcessAccordingToRelevanceEstimation:
                                pendingCategory = monitoringProcessFromAgentCat + "+"  # the "+" here represents the positive estimation, not necessarily correct (it is TBD when the quiz result comes)
                        else:   # action was finally cancelled by the user - no SRL process happened
                            pass

                    elif True in [isinstance(evt, evtType) for evtType in [Custom.CEvtUserJudgingLearningJOL, Custom.CEvtUserFeelingKnowledgeFOK]]:
                        if separateMonitoringProcessAccordingToRelevanceEstimation:
                            if isinstance(evt, Custom.CEvtUserJudgingLearningJOL):  # adapt to the fact the parameter is not called the same way for the two events
                                level = evt.understandingLevel
                            else:
                                level = evt.knowledgeLevel
                            # add a sign to represent the evaluation performed by the user associated to the JOL or FOK
                            if int(level) in [1, 2, 3]:
                                pendingCategorySuffix = "-"
                            elif int(level) in [4, 5, 6]:
                                pendingCategorySuffix = "+"
                            else:
                                self.logger.warning("Unknown user estimation value for " + str(evt) + ": " + str(level))
                                continue
                        if evt.MTEvent.initiative == "user":
                            if separateMonitoringProcessAccordingToRelevanceEstimation:
                                pendingCategory = monitoringProcessFromUserCat + pendingCategorySuffix
                            else:
                                eventCodeSequences[subjID].append(monitoringProcessFromUserCat)
                                dictAct[monitoringProcessFromUserCat] += 1
                        elif evt.MTEvent.initiative == "agent":
                            if separateMonitoringProcessAccordingToRelevanceEstimation:
                                pendingCategory = monitoringProcessFromAgentCat + pendingCategorySuffix
                            else:
                                eventCodeSequences[subjID].append(monitoringProcessFromAgentCat)
                                dictAct[monitoringProcessFromAgentCat] += 1
                        else:
                            self.logger.warning("Unknown initiative for " + str(evt) + ": " + str(evt.initiative))

                    elif isinstance(evt, Custom.CEvtUserEvaluatingContentCE):
                        CEsuffix = ""
                        if separateMonitoringProcessAccordingToRelevanceEstimation: # use a suffix to indicate if the user estimate correctly the relevance of the page
                            #if user claimed page wasn't (resp. was) relevant when it indeed wasn't (resp. was)
                            if ((evt.evaluatedRelevance == "None"  and evt.MTEvent.realRelevancy == False) or (evt.evaluatedRelevance != "None" and evt.MTEvent.realRelevancy == True)):
                                CEsuffix = "+"
                            else:
                                CEsuffix = "-"
                        if evt.MTEvent.initiative == "user":
                            eventCodeSequences[subjID].append(monitoringProcessFromUserCat + CEsuffix)
                            dictAct[monitoringProcessFromUserCat + CEsuffix] += 1
                        elif evt.MTEvent.initiative == "agent":
                            eventCodeSequences[subjID].append(monitoringProcessFromAgentCat + CEsuffix)
                            dictAct[monitoringProcessFromAgentCat + CEsuffix] += 1
                        else:
                            self.logger.warning("Unknown initiative for " + str(evt) + ": " + str(evt.initiative))

                    elif isinstance(evt, Custom.CEvtUserTakingQuiz):
                        success = (3 * evt.score >= 2 * evt.scoreMax) # true, if score is equal or above 2/3 of maxScore (i.e. 2 or 3 correct answers out of 3 questions) - false otherwise (i.e. 0 or 1 correct answers)
                        if (separateMonitoringProcessAccordingToRelevanceEstimation and evt.scoreMax == 3): # in that case, there is a pending event requiring the comparison of the estimation with the effective result on the page quiz (hence the check that there were 3 questions)
                            if ((pendingCategory[-1] == "+" and success) or (pendingCategory[-1] == "-" and not success)):    # estimated success (resp. failure) and effective success (resp. failure)
                                pendingCategory = pendingCategory[:-1] + "+"    # good estimation
                            elif ((pendingCategory[-1] == "-" and success) or (pendingCategory[-1] == "+" and not success)):    # estimated success (resp. failure) but effective failure (resp. success)
                                pendingCategory = pendingCategory[:-1] + "-"    # bad estimation
                            else:
                                self.logger.warning("Unexpected configuration of estimation (" + pendingCategory + ") and quiz result (" + success + ")")
                            eventCodeSequences[subjID].append(pendingCategory)
                            dictAct[pendingCategory] += 1
                            pendingCategory = ""    # reinitialize the pending category which has been treated
                            # in any case, also create a quiz action
                            if not QuizSeparateNAndP:
                                eventCodeSequences[subjID].append("Quiz")
                                dictAct["Quiz"] += 1
                            else:
                                if success: # if score is equal or above 2/3 of maxScore
                                    eventCodeSequences[subjID].append("QuizP")
                                    dictAct["QuizP"] += 1
                                else:   # if score is below 2/3 of maxScore (i.e. 0 or 1 for the 3 questions quizzes)
                                    eventCodeSequences[subjID].append("QuizN")
                                    dictAct["QuizN"] += 1

                    elif isinstance(evt, Browsing.MTBrowsingPageEvent):
                        pageRelevant = (float(evt.relevantToSubgoal) >= 0.5)    # count page as relevant if there is a subgoal and that it's either relevant or partially relevant
                        pageRelevancyRelevant = (currentSG not in ["0", 0]) # if no subgoal is currently set, page relevance information is not relevant
                        pageLong = (evt.timeSpentOverall >= datetime.timedelta(seconds=readLongShortThreshold))
                        if separateReadAccordingToRelevance and separateReadAccordingToDuration:
                            if pageLong:
                                if pageRelevancyRelevant:
                                    category = "ReadLR" if pageRelevant else "ReadLI"
                                else:
                                    category = "ReadL0"
                            else:
                                if pageRelevancyRelevant:
                                    category = "ReadSR" if pageRelevant else "ReadSI"
                                else:
                                    category = "ReadS0"
                        elif separateReadAccordingToRelevance:
                            if pageRelevancyRelevant:
                                category = "PageR" if pageRelevant else "PageI"
                            else:
                                category = "Page0"
                        elif separateReadAccordingToDuration:
                            category = "PageL" if pageLong else "PageS"
                        else:
                            category = "Read"
                        eventCodeSequences[subjID].append(category)
                        dictAct[category] += 1

                    elif isinstance(evt, Custom.CEvtPursuingNewSubgoal):
                        currentSG = evt.currentSubgoalID    # store the subgoal ID, really only to know if a subgoal is active or not

            #--- STEP 5: if requested, merge sequences of similar actions together using the suffix "-MULT"
            if mergeSequenceOfSameActionAsMult:
                eventCodeGroupedSequences = {}
                for subj in eventCodeSequences.keys():
                    eventCodeGroupedSequences[subj] = []
                    previousAction = ""
                    for action in eventCodeSequences[subj]:
                        #print "N: " + str(action) + "\t\tP: " + str(previousAction)
                        if action != previousAction:   # new action: just add it
                            eventCodeGroupedSequences[subj].append(action)
                            previousAction = action
                        else:                                     # same as previous action: replace it as a MULT and don't count
                            if eventCodeGroupedSequences[subj][-1][-4:] != "MULT":  # only if a MULT hasn't been added already
                                eventCodeGroupedSequences[subj][-1] = eventCodeGroupedSequences[subj][-1] + "-MULT"
                dataFinal = eventCodeGroupedSequences
                print("BEF-MULT:" + str(eventCodeSequences))
                print("AFT-MULT:" + str(eventCodeGroupedSequences))
            else:
                dataFinal = eventCodeSequences

            # build a string out of the event, to be exported into a file
            self.logger.info(str(dataFinal))
            dataFinalstr = ""
            for s in dataFinal.keys():
                for ie, e in enumerate(dataFinal[s]):
                    self.logger.info(str(e))
                    if mergeActionsInASingleString and ie != 0:     # ie!=0 to keep the participant ID in a separate cell
                        dataFinalstr += e + ";"
                    else:
                        dataFinalstr += e + "\t"
                dataFinalstr = dataFinalstr[:-1] + "\n"
            # export the data
            Utils.exportString2Excel(dataFinalstr, samplesID[igroup][1] + "-w" + ("o" if not mergeSequenceOfSameActionAsMult else "") +  "MULT.csv")


    @staticmethod
    def tmptest():
        return "test ok"
