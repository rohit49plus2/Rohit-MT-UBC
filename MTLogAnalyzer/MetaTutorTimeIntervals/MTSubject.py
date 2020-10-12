'''
Created on 2012-10-12

@author: Francois
'''

#import fileinput
import datetime
import time
from Events import *
import sys
#from MetaTutor.loganalyzer.MTLogAnalyzer import matTestPageDict, matPageSubgoalDict, nbSubgoalsSetInitially, nbMaxSubgoalsInStudy, calculateLearningGain, calculateLearningGainWithoutLosses
#import MetaTutor.loganalyzer
from Utils import Utils


class MTSubject(object):
    """Class grouping all the information collected for a participant, including in particular the content of his/her sessions with MetaTutor"""
    timeOffsetSubj = {"23003":[47, "???"],
                      "33019":[74, 69],
                      "33025":["???", 117.5],
                      "33038":["???", 77],
                      "33043":[63, "???"],
                      "33056":["???", 58.5]}
    """Dictionary of time differences in seconds between the beginning of the video file and the beginning of the MetaTutor log recording. Elements of the form: {subjectID:[ScreenCaptureOffset,WebcamOnlyOffset]}. A positive offset means MT is launched AFTER the start of the video, which should always be the case."""
    checkedIDsForNameDifferenceBetweenDays = ["23009", "23015", "23044", "MT21PN33013", "34032", "34091", "34102"]
    """IDs for which the name for day 1 and day 2 is known to be different (i.e. it has been checked manually by a human), in order to avoid a warning while processing data"""
    checkedIDsForPenOnAtTheEnd = ["33001", "33023", "34113"]
    """IDs for which the participant ends up with a non-empty queue containing a 'CEvtNoteTakenOnPaper' event, triggered because the participant dropped the pen on the Digimemo at the end (after the post test).
    Those have been checked manually by a human in order to confirm it's what they did, and therefore that ultimate event shouldn't trigger any warning message."""

    """Participant of a MT study"""
    def __init__(self, logger, ID, name, experimenter, otherdata, logLOD, logEvents, nbMaxSubgoalsInStudy, nbSubgoalsSetInitially):
        #self.logger = logger
        self.ID = ID
        # Retrieve the study from the participant ID
        if "23" in ID[:-2]:
            self.study = "MT2"
        elif ("33" in ID[:-2] or "34" in ID[:-2]):  # 33 for McGill, 34 for Memphis
            self.study = "MT3"
        elif ("41" in ID[:-2] or "42" in ID[:-2] or "44" in ID[:-2]):  # 41 for McGill, 42 for IIT, 44 for McGill medicine students
            self.study = "MT4"
        elif ("45" in ID[:-2] or "46" in ID[:-2]): # 45 for McGill, 46 for IIT
            self.study = "MT4.5"
        else:
            self.study = "Unknown"
            logger.warning("Participant " + self.ID + " study couldn't be determined from its ID")

        self.group = "Unknown"  # is known only when parsing day 2 log
        """Name of the group (or condition) the participant belongs to"""

        self.name = name
        self.experimenters = [experimenter, ""]
        if otherdata[0] == "0":
            self.thinkaloud = False
        else:
            self.thinkaloud = True
        self.logLOD = logLOD;
        """Level of details: 0 before 1.1.21, 1 for 1.1.21 including demographics info, 2 for 1.2.8 including screen resolution and no SRL quiz"""
        offset = 0
        if (logLOD >= 2):   # to take into account the extra line with the screen resolution
            offset += 1
        if (logLOD > 0):        # in cases where the summary log is detailed enough to have those info
            self.gender = otherdata[1+offset]
            self.age = otherdata[3+offset]
            self.ethnicity = otherdata[2+offset]
            self.education = otherdata[4+offset]
            self.GPA = otherdata[7+offset]
            self.major = otherdata[6+offset]
            self.school = otherdata[5+offset]
            self.courses = [[otherdata[8+offset], otherdata[9+offset], otherdata[10+offset]], [otherdata[11+offset], otherdata[12+offset], otherdata[13+offset]], [otherdata[14+offset], otherdata[15+offset], otherdata[16+offset]], [otherdata[17+offset], otherdata[18+offset], otherdata[19+offset]], [otherdata[20+offset]]]
            """previous knowledge, with the format [[[classTitle], [classNumber], [classComment]], ..., [otherRelevantWork]]"""
            self.nbCourses = 0
            self.countCourses()
            nextdataID = 21+offset
        else:
            self.gender = "N/A"
            self.age = "N/A"
            self.ethnicity = "N/A"
            self.education = "N/A"
            self.GPA = "N/A"
            self.major = "N/A"
            self.school = "N/A"
            self.courses = "N/A"
            self.nbCourses = -1
            nextdataID = 1
        self.day1File = otherdata[nextdataID]
        """the filename for day 1 log"""
        self.day1Events = logEvents
        """the list of MTEvent objects in the day 1"""
        self.SRL = {"PLAN":0, "SUMM":0, "TN":0, "MPTG":0, "RR":0, "COIS":0, "PKA":0, "JOL":0, "FOK":0, "CE":0, "INF":0, "DEPENDS":0, "Unknown":0}
        """the dictionary counting each kind of SRL event"""
        self.SRLPagesRelevantSubgoalWhenActive = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}, 7:{}}
        """the number of SRL processes done on each opened page when the page was relevant to the active subgoal, for each subgoal"""
        self.SRLPagesRelevantSubgoalAnytime = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}, 7:{}}
        """the number of SRL processes done on each opened page for each subgoal, at any time in the session, regardless of the active one at that time (can lead to duplicates for pages relevant to more than one subgoal)"""

        self.testsVersion = ["unknown", "unknown"]
        """the pretest and posttest version - should be A or B, and is determined while analyzing day 1 replies"""
        self.testsIndividualQuestionsScore = [[], []]
        """the score for each individual question for the pretest and posttest"""
        self.testsScoreRaw = [0, 0]
        """the scores obtained during the day 1/2 (out of 25)"""
        self.testsScoreRawFiltered = [0, 0]
        """the scores obtained during the day 1/2, excluding a predefined set of questions from pre/post-test"""
        self.testsMaxScoreRawFiltered = [0, 0]
        """the number of questions considered after exclusion of a predefined set of questions from pre/post-test"""
        self.testsScoreRelativeOpenedPages = [0, 0]
        """the score obtained during the day 1/2 tests, relative to the pages opened during the learning session (i.e. if a question is relative to a page not opened, its reply is discarded)"""
        self.testsMaxScoreOpenedPages = [0, 0]
        """the number of questions in the pre/post-test that were relative to a page opened during the learning session"""
        self.testsScoreRelativeReadLongPages = [0, 0]
        """the score obtained during the day 1/2 tests, relative to the pages that have been read for a long time during the learning session (i.e. if a question is relative to a page not opened or opened for less than 15s, its reply is discarded)"""
        self.testsMaxScoreReadLongPages = [0, 0]
        """the number of questions in the pre/post-test that were relative to a page read for more than 15s during the learning session"""
        self.testsScoreRelativeSubgoalPursued = [0, 0]
        """the score obtained during the day 1/2 tests, relative to the subgoal set and actively pursued during the learning session"""
        self.testsMaxScoreSubgoalPursued = [0, 0]
        """the number of questions in the pre/post-test that were relative to a subgoal actively pursued during the learning session"""
        self.nbMaxSubgoalsInStudy = nbMaxSubgoalsInStudy[self.study]
        """the maximum number of subgoals the participant could set in the study"""
        self.nbSubgoalsSetInitially = nbSubgoalsSetInitially[self.study]
        """the number of subgoals the participant had to set in the initial subgoal setting phase"""
        self.testsScoreRelativeAllSubgoals = [[0 for _ in range(self.nbMaxSubgoalsInStudy)] for _ in range(2)]
        """the score obtained during day 1/2 tests, relative to all the subgoals available"""
        self.testsMaxScoreAllSubgoals = [[0 for _ in range(self.nbMaxSubgoalsInStudy)] for _ in range(2)]
        """the number of questions in the pre/post-test that were relative to each of the subgoals in the system"""
        self.testsScoreRelativeSubgoalSet = [0, 0]
        """the score obtained during the day 1/2 tests, relative to the subgoals set"""
        self.testsMaxScoreSubgoalSet = [0, 0]
        """the number of questions in the pre/post-test that were relative to one of the subgoals set"""
        self.testsScoreRelativeSubgoalSetInitially = [[0 for _ in range(self.nbSubgoalsSetInitially)] for _ in range(2)]
        """the score obtained during the day 1/2 tests, relative to the subgoals set during the initial SG setting phase"""
        self.testsMaxScoreSubgoalSetInitially = [[0 for _ in range(self.nbSubgoalsSetInitially)] for _ in range(2)]
        """the number of questions in the pre/post-test that were relative to one of the subgoals set during the initial SG setting phase"""
        self.testsScoreRelativeSubgoalSetInitiallyFiltered = [[0 for _ in range(self.nbSubgoalsSetInitially)] for _ in range(2)]
        """the score obtained during the day 1/2 tests, relative to the subgoals set during the initial SG setting phase, excluding a predefined set of questions from pre/post-test"""
        self.testsMaxScoreSubgoalSetInitiallyFiltered = [[0 for _ in range(self.nbSubgoalsSetInitially)] for _ in range(2)]
        """the number of questions in the pre/post-test that were relative to one of the subgoals set during the initial SG setting phase, excluding a predefined set of questions from pre/post-test"""
        self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered = [0, 0]
        """the score obtained during the day 1/2 tests, relative to ALL the subgoals set during the initial SG setting phase, excluding a predefined set of questions from pre/post-test"""
        self.testsMaxScoreAllSubgoalsSetInitiallyFiltered = [0, 0]
        """the number of questions in the pre/post-test that were relative to ALL the subgoals set during the initial SG setting phase, excluding a predefined set of questions from pre/post-test"""
        self.testsScoreRelativeAllSubgoalsSetInitially = [0, 0]
        """the score obtained during the day 1/2 tests, relative to ALL the subgoals set during the initial SG setting phase"""
        self.testsMaxScoreAllSubgoalsSetInitially = [0, 0]
        """the number of questions in the pre/post-test that were relative to ALL the subgoals set during the initial SG setting phase"""

        self.nbSubgoalsAttempted = 0
        """number of different subgoals the participant explicitly (using the interface) tried to pursue (max = 7 - the fake subgoal 0 is not counted here)"""
        self.nbSubgoalsValidated = 0
        """number of different subgoals for which the participant has passed the associated quiz at least once (max = 7 - the fake subgoal 0 can't be counted here)"""
        self.workedWithoutSubgoals = False
        """has the participant ever been working without subgoals?"""
        self.nbSubgoalChanges = 0
        """number of times the participant said they were working on a new subgoal
        (can be more than 7, if one alternates between subgoal and doesn't systematically attempt to validate its acquisition with the subgoal quiz)"""
        self.subgoalChanges = []
        """list of changes of the participant's current subgoal"""
        self.subgoalsSet = []
        """list of subgoals the participant has set"""
        self.quizPageScoreRelevantSubgoalAnytime = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}
        """score on page quizzes for page relevant to each subgoal (regardless of the active one when quiz is taken).
        For pages relevant to more than one subgoal, it is counted once for each relevant subgoal"""
        self.quizPageScoreRelevantSubgoalWhenActive = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}
        """score on page quizzes when page was relevant to the ongoing subgoal, for each subgoal"""
        self.quizPageNb = 0
        """number of page quizzes taken (should be the sum of FOK and JOL)"""
        self.quizPageMeanScore = 0
        """mean score on the page quizzes"""
        self.quizPageWeightedMeanScore = 0
        """weighted mean score on page quizzes, using constant weights from scoreWeightsForQuizAnswers"""
        self.quizPageMeanScoreFirst = 0
        """mean score on the page quizzes, the first time they have been taken for each page (i.e. we ignore the scores after the first quiz for a page)"""
        self.quizPageWeightedMeanScoreFirst = 0
        """weighted mean score on page quizzes the first time they have been taken for each page, using constant weights from scoreWeightsForQuizAnswers"""
        self.quizSubgoalScore = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}
        """score obtained when taking the quiz associated to each subgoals (possibly multiple time for each subgoal)"""
        self.quizSubgoalWeightedScore = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}
        """weighted score obtained when taking the quiz associated to each subgoals (possibly multiple time for each subgoal)"""
        self.quizSubgoalNb = 0
        """number of subgoal quizzes taken"""
        self.quizSubgoalMeanScore = 0
        """mean score on the subgoal quizzes"""
        self.quizSubgoalWeightedMeanScore = 0
        """weighted mean score on the subgoal quizzes, using constant weights from scoreWeightsForQuizAnswers"""
        self.quizSubgoalMeanScoreFirst = 0
        """mean score on the subgoal quizzes, the first time they have been taken for each subgoal
        (the meaning is different from the page counterpart, because there is a minimum score to obtain for subgoal quizzes to be able to move on to the next one)"""
        self.quizSubgoalWeightedMeanScoreFirst = 0
        """weighted mean score on the subgoal quizzes the first time they have been taken for each subgoal, using constant weights from scoreWeightsForQuizAnswers"""

        self.relevancePageVisitSubgoalsWhenActive = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}
        """relevance of all the pages visited, in order of their visit, relatively to the subgoal that was active at that time"""
        self.ratioPagesRelevantToInitialSubgoalsVisitActive = []
        self.relevancePageReadSubgoalsAnytime = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}
        """relevance of all the pages visited for more than 15s, at any time in the session regardless of the active subgoal at that time, relatively to any of the subgoals"""
        self.ratioPagesRelevantToInitialSubgoalsReadAnytime = []
        self.relevancePageReadInitialSubgoalsAnytime = []
        """relevance of all the pages visited for more than 15s, at any time in the session regardless of the active subgoal at that time, relatively to any of the initial subgoals
        (i.e. counted as relevant if it was relevant to at least one of the initial subgoals)"""
        self.ratioPagesRelevantToAnyInitialSubgoalsReadAnytime = 0
        """ratio of pages relevant to any of the initial subgoals visited for more than 15s at any time in the session (regardless of the active subgoal), relatively to the total number of pages that were relevant to those subgoals (i.e. 1 means all relevant have been visited at some point)"""
        self.relevancePageReadSubgoalsWhenActive = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}
        """relevance of all the pages visited for more than 15s to subgoal N, if page was visited when subgoal N was active"""
        self.ratioPagesRelevantToInitialSubgoalsReadActive = []
        self.relevancePageReadInitialSubgoalsWhenActive = []
        """relevance of all the pages visited for more than 15s when one of the (two or three) initially set subgoal was active (i.e. don't consider time when any subgoal other than an initially set one is active),
        relatively to any of those initial subgoal (i.e. it doesn't have to be *the* active subgoal)"""
        self.ratioPagesRelevantToAnyInitialSubgoalsReadWhenActive = 0
        """ratio of pages relevant to any of the initial subgoals visited for more than 15s while working on any of them, relatively to the total number of pages that were relevant to those subgoals (i.e. 1 means all relevant pages have been visited and is the "best" value)"""
        self.ratioPagesIrrelevantToAnyInitialSubgoalsReadWhenActive = 0
        """ratio of pages irrelevant to any of the initial subgoals visited for more than 15s while working on any of them, relatively to the total number of pages that were irrelevant to those subgoals (i.e. 0 means all irrelevant pages have been avoided and is the "best" value)"""

        self.nbNoteTaking = 0
        """number of times the participant took some notes"""
        self.nbNoteChecking = 0
        """number of times the participant checked some notes"""
        self.nbNoteSummaryAdd = 0
        """number of times the participant agreed to add a summary to notes - should be deducted from nbNoteChecking for a more accurate number"""
        self.noteTakingDuration = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
        """total time spent taking notes (as a datetime)"""
        self.noteCheckingDuration = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
        """total time spent checking notes (as a datetime)"""
        self.sessionDuration = datetime.datetime(2000, 1, 1, 2, 0, 0, 0) - datetime.datetime(2000, 1, 1, 0, 0, 0, 1)
        """time spent in the learning session, i.e. between the moment when the 3 initial subgoals have been set up and when the participant starts the posttest"""
        self.readingDuration = datetime.datetime(2000, 1, 1, 2, 0, 0, 0)
        """time spent reading content in MetaTutor (session duration - (time for SRL processes + notes on paper + videos))"""
        self.learningSessionStartTime = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
        """time in the MetaTutor reference when the learning session started (i.e. when the timer is restarted to 60 minutes in study 4+)"""

        self.pagesOpened = []
        """IDs of pages opened (even if only for 1s) by the student during the learning session"""
        self.pagesReadShort = []
        """IDs of pages opened for 1 to 15s"""
        self.pagesReadLong = []
        """IDs of pages opened for more than 15s"""

        if self.ID in self.timeOffsetSubj:
            self.timeOffset = self.timeOffsetSubj[self.ID]
            """the offset in seconds for the screen capture (face + eyetracking) and the webcam only videos time reference, relatively to the MT log time reference"""
        else:
            self.timeOffset = [0, 0]
        self.subCounter = 0
        """subtitle counter (incremented before its first use)"""

        self.day1ExtEvents = []
        """extended events for the day 1 of the experiment"""
        self.day2ExtEvents = []
        """extended events for the day 2 of the experiment"""


        # --------------bondaria
        # The following was added in APril by Daria Bondareva
        #To Calculate time each user spent with page open to the relevant subgoal
        self.pagesTotalTimeSpentWithContent = datetime.timedelta(0,0,0)
        """Total time user spent with content. Questionnaires, Video, JOL, PKA, Quizzes are excluded"""
        self.pageTotalTimeOverall = datetime.timedelta(0,0,0)
        """Total time user spent with content. Includes Questionnaires, Videos, PKA, JOLs, Quizzes """
        self.pagesTotalTimeSpentRelevantSG = datetime.timedelta(0,0,0)
        """Total time user spent with content that is relevant to the current SG. Questionnaires, Video, JOL, PKA, Quizzes are excluded"""
        self.pagesTotalTimeSpentIrrelSG = datetime.timedelta(0,0,0)
        """Total time user spent with content that is irrelevant to the current SG. Questionnaires, Video, JOL, PKA, Quizzes are excluded"""
        self.pagesTimeProportionSGRel = 0.0
        """ Proportion of time user spent with content that is relevant to the goal over total time spent with content (relevant or irrelevant)"""
        self.pagesTimeProportionSGIrrel = 0.0
        """ Proportion of time user spent with content that is irrelevant to the goal over total time spent with content (relevant or irrelevant)"""

        self.SGTimeTotal = datetime.timedelta(0,0,0)
        """Total time spent on setting subgoal. Includes 3 initial subgoals and all optional subgoals (if any)"""
        self.SGTimeAVG = datetime.timedelta(0,0,0)
        """Average time spent on setting subgoal. Includes 3 initial subgoals and all optional subgoals (if any)"""

        self.NbSGTotal = 0
        """Number of subgoals set by user during the session. Includes 3 initial subgoals and all optional subgoals (if any)"""

        self.DurationNoteTakenOnPaper = datetime.timedelta(0, 0, 0)
        """Total time spent on taking notes using digital notepad"""
        self.DurationUserTypingINF = datetime.timedelta(0,0,0)
        """Total time spent on making inference"""
        self.DurationUserTypingPKA = datetime.timedelta(0,0,0)
        """Total time spent on typing prior knwoledge"""
        self.DurationUserTypingSummary = datetime.timedelta(0,0,0)
        """Total time spent on typing summary"""
        self.DurationDay2 = datetime.timedelta(0,0,0)
        """Duration of session during day2"""
        self.DurationMTInteractionDay2 = datetime.timedelta(0,0,0)
        """DUration Of session during day 2 excluding Video and Questionnaire """
        #the following two features correspond to Full Content vs. Text-Only Content available on screen
        self.timeSpentWithContentImage = datetime.timedelta(0, 0, 0)
        """Time spent on the page (with Image Open) after this event, minus time spent on questionnaires, watching videos and system pauses (can only be determined a posteriori, through an analysis)"""
        self.timeSpentWithContentNoImage = datetime.timedelta(0, 0, 0)
        """Time spent on the page (with No Image Open) after this event, minus time spent on questionnaires, watching videos and system pauses (can only be determined a posteriori, through an analysis)"""
        #the following FOUR features correspond to Full Content vs. Text-Only Content available on screen + Relevant to SG or Not Relevant to SG
        self.timeSpentWithContentImageRel = datetime.timedelta(0, 0, 0)
        """Time spent on the page (with Image Open) after this event, minus time spent on questionnaires, watching videos and system pauses (can only be determined a posteriori, through an analysis)"""
        self.timeSpentWithContentNoImageRel = datetime.timedelta(0, 0, 0)
        """Time spent on the page (with No Image Open) after this event, minus time spent on questionnaires, watching videos and system pauses (can only be determined a posteriori, through an analysis)"""

        self.timeSpentWithContentImageIrrel = datetime.timedelta(0, 0, 0)
        """Time spent on the page (with Image Open) after this event, minus time spent on questionnaires, watching videos and system pauses (can only be determined a posteriori, through an analysis)"""
        self.timeSpentWithContentNoImageIrrel = datetime.timedelta(0, 0, 0)
        """Time spent on the page (with No Image Open) after this event, minus time spent on questionnaires, watching videos and system pauses (can only be determined a posteriori, through an analysis)"""

        self.numImagesOpen = 0
        """Number  of images opened by student"""

        self.TimeFullView_total = datetime.timedelta(0, 0, 0)
        """Duration of staying on FullView layout"""

        #self.pagesTotalTimeSpentRelevantSG = 0

        #-----------------------------

        # Retrieve the offset for this particular subject from the dictionary (if it exists)
        try:
            self.videoFaceOffset = MTSubject.timeOffsetSubj[self.ID][1]
            self.videoScreenFaceOffset = MTSubject.timeOffsetSubj[self.ID][0]
        except KeyError:
            pass

    def countCourses(self):
        """Count the number of relevant courses the subject has followed and change the value of the corresponding attribute"""
        if self.courses != None:
            for course in self.courses:
                if course[0] != "":
                    self.nbCourses += 1

    def countSRLEvents(self):
        """Extract the SRL events from the list of events and use an attribute of the subject to count them"""
        for event in self.day2Events:
            # Check if the event or its parent is a MTRuleSRLEvent
            if isinstance(event, Rule.MTRuleSRLEvent):
                self.SRL[event.SRLType] += 1

    #-----bondaria
    def calculateTimeSpentSettingSG(self):
        "Calculate Total Time User spent on setting Subgoals"
        #day2ExtEvents
        for event in self.day2ExtEvents:
            if isinstance(event, Custom.CEvtSubgoalSetting):
                #corresponds to setting new voluntory subgoal
                print("Optional Subgoal setting detected ... Processing")
                self.SGTimeTotal += event.timeEnd - event.timeStart
                self.NbSGTotal += 1
                self.SGTimeAVG = self.SGTimeTotal / self.NbSGTotal
            if isinstance(event, Custom.CEvtInitialSubgoalsSetting):
                #calculates time on setting two initial compulsory subgoals
                print( "Initial Subgoal setting detected ... Processing")
                self.SGTimeTotal += event.timeEnd - event.timeStart
                self.NbSGTotal += 2
                self.SGTimeAVG = self.SGTimeTotal / self.NbSGTotal


        return
    #-----bondaria
#    def calculateTimePagesOpenRelevantSG(self):
#        """Calculate time when User was has page Relevant to the active SG Open"""
#        for event in self.day2Events:
#            if isinstance(event, Browsing.MTBrowsingPageEvent):
#                #print event.pageTitle
#                self.pagesTotalTimeSpentWithContent += event.timeSpentWithContent
#                self.pageTotalTimeOverall +=event.timeSpentOverall
#                if event.relevantToSubgoal > 0: #partially related or fully related
#                    self.pagesTotalTimeSpentRelevantSG += event.timeSpentWithContent
#                self.pagesTimeProportionSGRel = 1.0 * self.pagesTotalTimeSpentRelevantSG.seconds / self.pagesTotalTimeSpentWithContent.seconds
#
    #-----bondaria
    def calculateTimePagesOpenRelevantSGImage(self):
        """Calculate time when User was has page Relevant to the active SG Open and if Image is open or not"""
        """This function takes into account if the image was opened or not!"""
        for event in self.day2Events:
            #if isinstance(event, Browsing.MTBrowsingImageEvent):
                #print event.imageName
                #print event.timestamp
                #print event.absoluteTime
            if isinstance(event, Browsing.MTBrowsingPageEvent):
                self.pagesTotalTimeSpentWithContent += event.timeSpentWithContent
                self.pageTotalTimeOverall +=event.timeSpentOverall
                if event.relevantToSubgoal > 0: #partially related or fully related
                    self.pagesTotalTimeSpentRelevantSG += event.timeSpentWithContent
                    self.timeSpentWithContentImageRel += event.timeSpentWithContentImageRel
                    self.timeSpentWithContentNoImageRel += event.timeSpentWithContentNoImageRel
                    self.timeSpentWithContentImage += event.timeSpentWithContentImage
                    self.timeSpentWithContentNoImage += event.timeSpentWithContentNoImage

                else:
                    self.pagesTotalTimeSpentIrrelSG += event.timeSpentWithContent
                    self.timeSpentWithContentImageIrrel += event.timeSpentWithContentImageIrrel
                    self.timeSpentWithContentNoImageIrrel = event.timeSpentWithContentNoImageIrrel
                    self.timeSpentWithContentImage += event.timeSpentWithContentImage
                    self.timeSpentWithContentNoImage += event.timeSpentWithContentNoImage

                try:
                    self.pagesTimeProportionSGRel = 1.0 * self.pagesTotalTimeSpentRelevantSG.seconds / self.pagesTotalTimeSpentWithContent.seconds
                    self.pagesTimeProportionSGIrrel = 1.0 * self.pagesTotalTimeSpentIrrelSG.seconds / self.pagesTotalTimeSpentWithContent.seconds
                except ZeroDivisionError:
                    self.pagesTimeProportionSGRel = "N/A"
                    self.pagesTimeProportionSGIrrel = "N/A"

                #self.timeSpentWithContentImage = datetime.timedelta(0, 0, 0)
                #self.timeSpentWithContentNoImage = datetime.timedelta(0, 0, 0)
            if isinstance(event, Browsing.MTBrowsingImageEvent):
            #calculate number of open images
                self.numImagesOpen += 1
    #def convertTimeDelta2Float(self, timed):
    #    """"this function converts TimeDelta format to Float"""
    #    return

    def TimeDelta2Miliseconds(self, td):
        return td.seconds * 1000 + td.microseconds/1000
    def AveragedOverX(self, feature, duration, NumNeedsConvert = True):
    #NumNeedsConvert - if Numerator is of type timedelta, it needs to be converted to miliseconds
        if NumNeedsConvert:
            return 1.0 * self.TimeDelta2Miliseconds(feature) / self.TimeDelta2Miliseconds(duration)
        else:
            return 1.0 * feature / self.TimeDelta2Miliseconds(duration)
    #------------------------

    def countExtraSRLEvents(self, logger, matPageSubgoal):
        """Extract the number of SRL events associated to each page relevant to the current subgoal"""
        evtslist = self.getEvents([Custom.CEvtPursuingNewSubgoal, Rule.MTRuleSRLEvent, Browsing.MTBrowsingPageEvent], 2)
        currentSubgoal = -1
        currentPage = -1
        srlInCurrentPage = False
        currentPageRelevant = False
        for evt in evtslist:
            if isinstance(evt, Custom.CEvtPursuingNewSubgoal):
                currentSubgoal = int(evt.currentSubgoalID)
                currentPageRelevant = (matPageSubgoal[currentSubgoal-1][currentPage] > 0)   # the page is relevant to the current subgoal
            elif isinstance(evt, Browsing.MTBrowsingPageEvent):
                if currentSubgoal==-1:
                    continue
                if not srlInCurrentPage:    # no SRL performed during this visit to the page
                    if currentPageRelevant:
                        if not currentPage in self.SRLPagesRelevantSubgoalWhenActive[currentSubgoal]: # the page had never been visited before
                            self.SRLPagesRelevantSubgoalWhenActive[currentSubgoal][currentPage] = 0   # save that no SRL has been performed on this page
                    for sgid, sg in enumerate(matPageSubgoal):
                        if sg[currentPage] > 0: # page relevant to that subgoal
                            if not currentPage in self.SRLPagesRelevantSubgoalAnytime[sgid+1]:
                                self.SRLPagesRelevantSubgoalAnytime[sgid+1][currentPage] = 0
                currentPage = int(evt.pageIdx)
                srlInCurrentPage = False
                currentPageRelevant = (matPageSubgoal[currentSubgoal-1][currentPage] > 0)   # the page is relevant to the current subgoal
            else:
                if currentPageRelevant: # record the process for the currently active subgoal if the page is relevant to it
                    srlInCurrentPage = True
                    if currentSubgoal==-1:
                        continue
                    if not currentPage in self.SRLPagesRelevantSubgoalWhenActive[currentSubgoal]:
                        self.SRLPagesRelevantSubgoalWhenActive[currentSubgoal][currentPage] = 1
                    else:
                        self.SRLPagesRelevantSubgoalWhenActive[currentSubgoal][currentPage] += 1
                # also record the process for each subgoal relevant to the current page, regardless of them being active or not
                for sgid, sg in enumerate(matPageSubgoal):
                    if sg[currentPage] > 0: # page relevant to that subgoal
                        if not currentPage in self.SRLPagesRelevantSubgoalAnytime[sgid+1]:
                            self.SRLPagesRelevantSubgoalAnytime[sgid+1][currentPage] = 1
                        else:
                            self.SRLPagesRelevantSubgoalAnytime[sgid+1][currentPage] += 1

        #print self.SRLPagesRelevantSubgoalWhenActive

    def computeExtraAttributes(self, logger, nonValidTestQuestions, nbSubgoalsSetInitially, nbPagesInSystem, matTestPageDict, matPageSubgoalDict, minNoteTime, stopTimeStamp=None, startTimeStamp=None):
        """Calculates some values after extended events have been generated"""
        self.countExtraSRLEvents(logger, matPageSubgoalDict[self.study])
        self.computeExtraPageVisitsAttributes(logger)
        self.computeExtraSubgoalsAttributes(logger)
        # need to be called after page visits and subgoals attributes have been computed
        #self.computeExtraPreTestAttributes(logger, nonValidTestQuestions, matTestPageDict[self.study], matPageSubgoalDict[self.study])
        #self.computeExtraPostTestAttributes(logger, nonValidTestQuestions, matTestPageDict[self.study], matPageSubgoalDict[self.study])
        #self.computeExtraQuizzesAttributes(logger, matPageSubgoalDict[self.study])
        self.computeExtraNotesAttributes(logger, minNoteTime)
        self.computeExtraDurationAttributes(logger, stopTimeStamp, startTimeStamp)
        self.computeExtraPageRelevanceAttributes(logger, nbSubgoalsSetInitially, nbPagesInSystem, matPageSubgoalDict[self.study])
        #-----bondaria
        #self.calculateTimePagesOpenRelevantSG()
        self.calculateTimePagesOpenRelevantSGImage()
        self.calculateTimeSpentSettingSG()
        evtslist = self.getEvents([Custom.CEvtUserTypingINF, Custom.CEvtUserTypingPKA, Custom.CEvtUserTypingSummary, Custom.CEvtNoteTakenOnPaper, Layout.MTLayoutEvent], 2)
        FlagFullView = False
        FullViewStart = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
        for evt in evtslist:    # substract to the duration of the session the duration of all the SRL events + time taken writing paper notes + time a video was playing, to obtain an estimation of the reading time
            if isinstance(evt, Custom.CEvtNoteTakenOnPaper):
                self.DurationNoteTakenOnPaper += evt.duration
            elif isinstance(evt, Custom.CEvtUserTypingINF):
                self.DurationUserTypingINF += evt.duration
            elif isinstance(evt, Custom.CEvtUserTypingPKA):
                self.DurationUserTypingPKA += evt.duration
            elif isinstance(evt, Custom.CEvtUserTypingSummary):
                self.DurationUserTypingSummary += evt.duration
            #calculate how long user spent in FullView layout
            elif isinstance(evt, Layout.MTLayoutEvent):
                if evt.layout == "FullView":
                    print("Full View")
                    FlagFullView = True
                    FullViewStart = evt.timestamp
                elif FlagFullView == True:
                    print( "FullView end")
                    self.TimeFullView_total += evt.timestamp - FullViewStart
                    FlagFullView = False
        #calculate duration of session without questionnaires and videos
        # IT USED TO BE: self.DurationDay2 = self.day2AllEvents[-1].timestamp - self.day2AllEvents[0].timestamp#duration of session during day 2

        #based on Daria:
        if not isinstance(self.day2AllEvents[-1], Custom.CEvent):
            timeend = self.day2AllEvents[-1].timestamp
        else:
            timeend = self.day2AllEvents[-1].timeEnd
        if not isinstance (self.day2AllEvents[0], Custom.CEvent):
            timestart = self.day2AllEvents[0].timestamp
        else:
            timestart = self.day2AllEvents[0].timeStart
        self.DurationDay2 = timeend - timestart

        self.DurationMTInteractionDay2 = self.DurationDay2

        #print self.ID, ": Duration of session day 2: ", self.DurationDay2
        evtslist = self.getEvents([Custom.CEvtVideoIsPlaying, Custom.CEvtQuestionnaireOngoing], 2)
        for evt in evtslist:    # substract to the duration of the session the duration of all the SRL events + time taken writing paper notes + time a video was playing, to obtain an estimation of the reading time
            self.DurationMTInteractionDay2 -= evt.duration
            #if isinstance(evt, Custom.CEvtVideoIsPlaying):
            #    print "Video: start - ", Utils.getMilliSecondsFromDatetime(evt.timeStart), ", end - ", Utils.getMilliSecondsFromDatetime(evt.timeEnd), " duration - ", evt.duration
            #else:
            #    print "Questionnaire: start - ", Utils.getMilliSecondsFromDatetime(evt.timeStart), ", end - ", Utils.getMilliSecondsFromDatetime(evt.timeEnd), " duration - ", evt.duration
        #print self.ID,": ",self.DurationMTInteractionDay2
        #----------------
    def computeExtraPageVisitsAttributes(self, logger):
        evtslist = self.getEvents([Browsing.MTBrowsingPageEvent], 2)
        for evt in evtslist:
            if (int(evt.pageIdx) not in self.pagesOpened):
                self.pagesOpened.append(int(evt.pageIdx))                   # register the page as opened
                if (evt.timeSpentWithContent > datetime.timedelta(seconds=15)):    # register the page as read for a short (resp. long) amount of time if less (resp. more) than 15s have been spent on it
                    self.pagesReadLong.append(int(evt.pageIdx))
                else:
                    self.pagesReadShort.append(int(evt.pageIdx))
        self.pagesOpened.sort()
        self.pagesReadShort.sort()
        self.pagesReadLong.sort()
        #print "Pages opened: " + str(self.pagesOpened)
#        print self.pagesReadShort
#        print self.pagesReadLong

    def computeExtraPreTestAttributes(self, logger, nonValidTestQuestions, matTestPage, matPageSubgoal):
        """Calculates various pretest scores"""
        self.computeExtraTestsAttributes(logger, self.getEvents([Custom.CEvtUserTakingPreTest], 1), "pre", nonValidTestQuestions, matTestPage, matPageSubgoal)

    def computeExtraPostTestAttributes(self, logger, nonValidTestQuestions, matTestPage, matPageSubgoal):
        """Calculates various post-test scores"""
        self.computeExtraTestsAttributes(logger, self.getEvents([Custom.CEvtUserTakingPostTest], 2), "post", nonValidTestQuestions, matTestPage, matPageSubgoal)

    def computeExtraTestsAttributes(self, logger, evtslist, testType, nonValidTestQuestions, matTestPage, matPageSubgoal):
        """Calculates different test scores"""
        if testType == "pre":
            idxScore = 0
        elif testType == "post":
            idxScore = 1
        else:
            logger.warning("Unknown type of test: " + testType)
            return

        idxTest = 0 if self.testsVersion[idxScore] == "A" else 1;  # get the index associated to the version of the post-test

        # Raw test score
#        print "XXXXX " + str(self.ID)
#        print "YYYY" + str(idxScore)
#        print self.testsScoreRaw
#        print evtslist
        self.testsScoreRaw[idxScore] = evtslist[0].score

        # Calculate the filtered score and individual questions score
        for idx, quizReply in enumerate(evtslist[0].quizEvents):
            self.testsIndividualQuestionsScore[idxScore].append(1 if quizReply.answerCorrect else 0)
            if (idx+1) not in nonValidTestQuestions[idxTest]:
                self.testsMaxScoreRawFiltered[idxScore] += 1
                if quizReply.answerCorrect:
                    self.testsScoreRawFiltered[idxScore] += 1

        # Test score relative to pages visited
        if (self.pagesOpened == []):
            logger.info("Participant doesn't seem to have visited any page - check that the visited page attributes have been calculated before calling this function")
            self.computeExtraPageVisitsAttributes(logger)

        for evt in evtslist[0].quizEvents:  # quiz events associated to each question of the (unique) post-test
            if (matTestPage[idxTest][int(evt.questionID[1:])-1] in self.pagesOpened): # if the page associated to this question has been visited
                self.testsMaxScoreOpenedPages[idxScore] += 1
                self.testsScoreRelativeOpenedPages[idxScore] += 1 if evt.answerCorrect else 0
            if (matTestPage[idxTest][int(evt.questionID[1:])-1] in self.pagesReadLong): # if the page associated to this question has been read for a long time
                self.testsMaxScoreReadLongPages[idxScore] += 1
                self.testsScoreRelativeReadLongPages[idxScore] += 1 if evt.answerCorrect else 0
#        print "Score Raw:\t" + str(self.postTestScore) + " / 25"
#        print "Score Ope:\t" + str(self.postTestScoreRelativeOpenedPages) + " / " + str(self.postTestMaxScoreOpenedPages)
#        print "Score RLo:\t" + str(self.postTestScoreRelativeReadLongPages) + " / " + str(self.postTestMaxScoreReadLongPages)

        # Test score relative to subgoals actively pursued (i.e. not only "set")
        if (self.subgoalChanges == []):
            self.computeExtraSubgoalsAttributes(logger)

        #print "XXXXX " + str(self.ID)
        #print self.subgoalsSet
        for questionId, evt in enumerate(evtslist[0].quizEvents):  # for each question of the test
            sgidx = 0
            sgChangeChecked = False
            sgSetChecked = False
            sgInitSetChecked = False
            for subgoalRelPage in matPageSubgoal:    # for each set of pages relevant to a subgoal
                sgidx += 1
                if (subgoalRelPage[matTestPage[idxTest][int(evt.questionID[1:])-1]] > 0): # if the page relative to the question is associated to the considered subgoal, count the question
                    self.testsMaxScoreAllSubgoals[idxScore][sgidx-1] += 1   # increment the max score for the current subgoal
                    self.testsScoreRelativeAllSubgoals[idxScore][sgidx-1] += 1 if evt.answerCorrect else 0  # increment the score associated to the current subgoal if the answer was correct
                    if (sgidx in self.subgoalsSet): # if this particular subgoal has been set
                        if (not sgSetChecked):
                            sgSetChecked = True # if it's relative to one of the subgoals set, that's enough, no need to check the others
                            self.testsMaxScoreSubgoalSet[idxScore] += 1
                            self.testsScoreRelativeSubgoalSet[idxScore] += 1 if evt.answerCorrect else 0

                        if ((self.subgoalsSet.index(sgidx)) + 1 <= self.nbSubgoalsSetInitially):     # if this is one of the initial subgoals
                            # subgoals are counted separately, so it's ok to go in there more than once per page (as a different SG would be incremented, if the page is relevant to more than one)
                            self.testsMaxScoreSubgoalSetInitially[idxScore][self.subgoalsSet.index(sgidx)] += 1
                            self.testsScoreRelativeSubgoalSetInitially[idxScore][self.subgoalsSet.index(sgidx)] += 1 if evt.answerCorrect else 0
                            if (questionId + 1) not in nonValidTestQuestions[idxTest]:  # if the question ID is not in the ones excluded, count it
                                self.testsMaxScoreSubgoalSetInitiallyFiltered[idxScore][self.subgoalsSet.index(sgidx)] += 1
                                self.testsScoreRelativeSubgoalSetInitiallyFiltered[idxScore][self.subgoalsSet.index(sgidx)] += 1 if evt.answerCorrect else 0

                            if (not sgInitSetChecked):
                                sgInitSetChecked = True # if it's relative ot one of the subgoals initially set, that's enough, no need to check the others initially set subgoals
                                self.testsMaxScoreAllSubgoalsSetInitially[idxScore] += 1
                                self.testsScoreRelativeAllSubgoalsSetInitially[idxScore] += 1 if evt.answerCorrect else 0
                                if (questionId + 1) not in nonValidTestQuestions[idxTest]:    # if the question ID is not in the ones excluded, count it
                                    self.testsMaxScoreAllSubgoalsSetInitiallyFiltered[idxScore] += 1
                                    self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[idxScore] += 1 if evt.answerCorrect else 0

                        if (sgidx in self.subgoalChanges and not sgChangeChecked):  # if this particular subgoal has been pursued (and count it only once for this question)
                            sgChangeChecked = True  # if it's relative to one of the subgoals pursued, that's enough, no need to check the others
                            self.testsMaxScoreSubgoalPursued[idxScore] += 1
                            self.testsScoreRelativeSubgoalPursued[idxScore] += 1 if evt.answerCorrect else 0

        #print "Initial SGs: " + str(self.subgoalsSet[:2])
        #print "Test version: "  + str(self.testsVersion[idxScore])
        #print "NonFiltered: \t" + str(self.testsMaxScoreSubgoalSetInitially)
        #print "Filtered: \t" + str(self.testsMaxScoreSubgoalSetInitiallyFiltered)

#            sgidx = 0
#            #print "Question " + str(int(evt.questionID[1:])-1) + " is associated to page " + str(MTLogAnalyzer.matTestPage[idxPostTest][int(evt.questionID[1:])-1])
#            for subgoalRelPage in MTLogAnalyzer.matPageSubgoal:    # for each set of pages relevant to a subgoal
#                sgidx += 1
#                if (sgidx in self.subgoalChanges):  # if this particular subgoal has been pursued
#                    if (subgoalRelPage[MTLogAnalyzer.matTestPage[idxTest][int(evt.questionID[1:])-1]] > 0):     # if the page relative to the question is associated to the considered subgoal, count the question
#                        #print "Page " + str(MTLogAnalyzer.matTestPage[idxPostTest][int(evt.questionID[1:])-1]) + " is associated to subgoal " + str(sgidx)
#                        self.testsMaxScoreSubgoalPursued[idxScore] += 1
#                        self.testsScoreRelativeSubgoalPursued[idxScore] += 1 if evt.answerCorrect else 0
#                        break   # if it's relative to one of the subgoal pursued, that's enough, no need to check the others
#
#            # do the same thing for subgoals set and subgoals set originally
#            sgidx = 0
#            #print "Question " + str(int(evt.questionID[1:])-1) + " is associated to page " + str(MTLogAnalyzer.matTestPage[idxPostTest][int(evt.questionID[1:])-1])
#            for subgoalRelPage in MTLogAnalyzer.matPageSubgoal:    # for each set of pages relevant to a subgoal
#                sgidx += 1
#                if (sgidx in self.subgoalsSet):  # if this particular subgoal has been set
#                    if (subgoalRelPage[MTLogAnalyzer.matTestPage[idxTest][int(evt.questionID[1:])-1]] > 0):     # if the page relative to the question is associated to the considered subgoal, count the question
#                        #print "Page " + str(MTLogAnalyzer.matTestPage[idxPostTest][int(evt.questionID[1:])-1]) + " is associated to subgoal " + str(sgidx)
#                        self.testsMaxScoreSubgoalSet[idxScore] += 1
#                        self.testsScoreRelativeSubgoalSet[idxScore] += 1 if evt.answerCorrect else 0
#                        if (self.subgoalsSet.index(sgidx)) + 1 <= MTLogAnalyzer.nbSubgoalsSetInitially:
#                            self.testsMaxScoreSubgoalSetInitially[idxScore] += 1
#                            self.testsScoreRelativeSubgoalSetInitially[idxScore] += 1 if evt.answerCorrect else 0
#                        break   # if it's relative to one of the subgoal pursued, that's enough, no need to check the others
#

#        print "Score SGp:\t" + str(self.postTestScoreRelativeSubgoalPursued) + " / " + str(self.postTestMaxScoreSubgoalPursued)

        # Test score relative to the 3 original subgoals (for studies 2 and 3) / 2 original subgoals (for study 4)

    def computeExtraSubgoalsAttributes(self, logger):
        """Calculates information about number of subgoals tried, change and validation"""
        # Subgoals attributes
        evtslist = self.getEvents([Custom.CEvtPursuingNewSubgoal], 2)
        evtslist2 = []
        # filter possible doublons
        prevsg = -1
        for e in evtslist:
            if e.currentSubgoalID != prevsg:
                evtslist2.append(e)
            prevsg = e.currentSubgoalID
        evtslist = evtslist2

        # Build the list of subgoals tried
        self.nbSubgoalChanges = len(evtslist)
        for evt in evtslist:
            if not evt.currentSubgoalID in self.subgoalChanges:
                self.subgoalChanges.append(evt.currentSubgoalID)
        #print "SGTRIED: " + str(self.subgoalChanges)

        if (self.subgoalChanges.count(0) > 0):
            self.nbSubgoalsAttempted = len(self.subgoalChanges) - 1
            self.workedWithoutSubgoals = True
            #print "Worked without subgoal!"
        else:
            self.nbSubgoalsAttempted = len(self.subgoalChanges)
            self.workedWithoutSubgoals = False
        if self.nbSubgoalsAttempted > self.nbMaxSubgoalsInStudy + 1:  # +1 because after the 3 initial subgoals, there is always a moment when participant works on the fake subgoal "0", when they don't have any subgoal set
            logger.warning("Participant has supposedly worked on more than " + str(self.nbMaxSubgoalsInStudy) + " different subgoals (" + str(self.nbSubgoalsAttempted) + ")")

        # Count number of subgoals actually validated, i.e. which resulted in pursuing a new subgoal OR where participants validated a subgoal but wanted to spend more time on it
        evtslist = self.getEvents([Custom.CEvtValidatedSubgoal], 2)
        evtslist2 = []
        for e in evtslist:
            if e.validatedSubgoalID != prevsg:
                evtslist2.append(e)
            prevsg = e.validatedSubgoalID
        self.nbSubgoalsValidated = len(evtslist2)

        # Build the list of subgoals set
        evtslist = self.getEvents([Custom.CEvtSubgoalSet], 2)
        for evt in evtslist:
            self.subgoalsSet.append(evt.subgoalID)

    def computeExtraQuizzesAttributes(self, logger, matPageSubgoal):
        """Calculates information about page and subgoal quizzes and different scores for them"""
        # Page quizzes attributes
        [self.quizPageNb, self.quizPageMeanScore, self.quizPageMeanScoreFirst, self.quizPageWeightedMeanScore, self.quizPageWeightedMeanScoreFirst] = self.computeQuizAttributes(logger, "Page", matPageSubgoal)
        #print self.computeQuizAttributes("Page")
        # Subgoal quizzes attributes
        [self.quizSubgoalNb, self.quizSubgoalMeanScore, self.quizSubgoalMeanScoreFirst, self.quizSubgoalWeightedMeanScore, self.quizSubgoalWeightedMeanScoreFirst] = self.computeQuizAttributes(logger, "Subgoal", matPageSubgoal)
        #print self.computeQuizAttributes("Subgoal")

    def computeQuizAttributes(self, logger, prefix, matPageSubgoal):
        """Calculates, for page or subgoal quizzes, the number of quizzes taken, the mean score and the mean score on the first try, as well as a weighted mean for those two last elements"""
        el = self.getEvents([Custom.CEvtUserTakingQuiz], 2)
        quiznb = 0
        quiz = {}
        quizscore = {}
        quizweightedscore = {}
        for e in el:
            idx = -1
            if (prefix == "Page" and e.page != None):
                idx = int(e.page)
                currentSubgoal = self.getSubgoalWhenEvent(logger, e)
                for sgid, sg in enumerate(matPageSubgoal): # for each subgoal
                    if sg[idx] > 0: # if the page is relevant
                        self.quizPageScoreRelevantSubgoalAnytime[sgid+1].append(e.score)
                        if sgid == currentSubgoal:  # if the subgoal is the active one
                            self.quizPageScoreRelevantSubgoalWhenActive[sgid+1].append(e.score)

            elif (prefix == "Subgoal" and e.subgoal != None):
                idx = int(e.subgoal)
                self.quizSubgoalScore[idx].append(e.score)
                self.quizSubgoalWeightedScore[idx].append(e.weightedScore)

            if (idx != -1):  # if it's an element relevant to the prefix
                quiznb += 1 # increment the quiz counter
                #print "id: " + str(idx) + "\t s: " + str(e.score) + "\t w:" + str(e.weightedScore)
                try:
                    quiz[idx] += 1                   # increment the quiz counter for a given element
                    quizscore[idx].append(e.score)    # append the number of points obtained for this quiz
                    quizweightedscore[idx].append(e.weightedScore)    # append the weighted score obtained for this quiz
                except KeyError:
                    quiz[idx] = 1                    # initialize the quiz counter for a given element
                    quizscore[idx] = [e.score]   # initialize with a list containing the number of points obtained for the first quiz on this element
                    quizweightedscore[idx] = [e.weightedScore]   # initialize with a list containing the weighted score obtained for this quiz
        if len(quiz) == 0:  # no quiz taken
            return [quiznb, 0, 0, 0, 0]
        else:
            #print quizscore
            meanscore = float(sum([x for sublist in quizscore.values() for x in sublist])) / sum(quiz.values())
            meanscorefirst = float(reduce(lambda x,y: x+y, map(lambda z: z[0], quizscore.values()))) / len(quiz)
            weightedmeanscore = float(sum([x for sublist in quizweightedscore.values() for x in sublist])) / sum(quiz.values())
            weightedmeanscorefirst = float(reduce(lambda x,y: x+y, map(lambda z: z[0], quizweightedscore.values()))) / len(quiz)
            return [quiznb, meanscore, meanscorefirst, weightedmeanscore, weightedmeanscorefirst]

    def computeExtraNotesAttributes(self, logger, minNoteTime):
        """Calculates information regarding number and duration of note-taking and note-checking (opening notes without adding any)"""
        evtslist = self.getEvents([Custom.CEvtNoteTakeGUI], 2)
        evtslistFiltered = []
        for evt in evtslist:
            if evt.duration > minNoteTime:
                self.noteTakingDuration += evt.duration
                evtslistFiltered.append(evt)
        self.nbNoteTaking = len(evtslistFiltered)

        evtslist = self.getEvents([Custom.CEvtNoteCheckGUI], 2)
        evtslistFiltered = []
        for evt in evtslist:
            if evt.duration > minNoteTime:
                self.noteCheckingDuration += evt.duration
                evtslistFiltered.append(evt)
        self.nbNoteChecking = len(evtslistFiltered)

        evtslist = self.getEvents([Custom.CEvtNoteAddedFromSummary], 2)
        self.nbNoteSummaryAdd = len(evtslist)

    def computeExtraDurationAttributes(self, logger, stopTimeStamp=None, startTimeStamp=None):
        """Calculates time spent in the learning session and time spent actually reading pages"""
        # Reading and session durations

        """if len(allevtslist) != 0:
            self.sessionDuration = allevtslist[-1].getTimeEnd()
            self.sessionDuration -= allevtslist[0].getTimeStart()
        elif stopTimeStamp != None and startTimeStamp != None:
            self.sessionDuration = stopTimeStamp - startTimeStamp
        else:
            self.sessionDuration = Event.Event.convertTimeMT2Standard(0)
            print "MTSubject.computeExtraDurationAttributes, using 0 as session Duration"
            time.sleep(5)"""

        """SHOULD GET STOP TIME STAMP!!!!!!!!!!! NOT NONE"""
        evtslist = self.getEvents([Custom.CEvtUserWaitingForPostTest], 2)
        if len(evtslist) != 0:
            self.sessionDuration = evtslist[-1].getTimeStart()
        else:
            self.sessionDuration = stopTimeStamp
        # print( "test:\t\t" + Event.Event.convertTimeStandard2String(self.sessionDuration))

        evtslist = self.getEvents([Custom.CEvtPursuingNewSubgoal], 2)
        if len(evtslist) != 0:
            self.sessionDuration -= evtslist[0].getTimeEnd()
        else:
            self.sessionDuration -= startTimeStamp
        print( "1st SG:\t")


        self.readingDuration = self.sessionDuration     # initialize the reading duration to the duration of the session, since it can't be superior to that
        evtslist = self.getEvents([Custom.CEvtUserTypingINF, Custom.CEvtUserTypingPKA, Custom.CEvtUserTypingSummary, Custom.CEvtVideoIsPlaying, Custom.CEvtNoteTakenOnPaper,
                                   Custom.CEvtUserEvaluatingContentCE, Custom.CEvtUserFeelingKnowledgeFOK, Custom.CEvtUserJudgingLearningJOL], 2)
        for evt in evtslist:    # substract to the duration of the session the duration of all the SRL events + time taken writing paper notes + time a video was playing, to obtain an estimation of the reading time
            self.readingDuration -= evt.duration
        # print "session: \t" + str(self.sessionDuration)
        # print "reading: \t" + str(self.readingDuration)
        # print "---"

        # Get the event which marks the beginning of the learning session (when timer is restarted at 60 minutes)
        # - normally, it is when the video "ManagingSGs.avi" starts, but since the time is paused while it's displayed, it means one can take the first agent talk after that,
        # which corresponds to Pam asking for the first SG PKA
        evtslist = self.getEvents([Agent.MTAgentTalkEvent], 2, around=False)
        for evt in evtslist:
            if evt.scriptID == "PamPKAPromptBeginningSubgoal":
                self.learningSessionStartTime = evt.timestamp
                break
        return

    def computeExtraPageRelevanceAttributes(self, logger, nbSubgoalsSetInitially, nbPagesInSystem, matPageSubgoal):
        """Calculates relevance of visited pages for: 1) the active subgoal,  2) the originally set subgoals, while working on any of them, with only one visit counted per page"""
        evtslist = self.getEvents([Browsing.MTBrowsingPageEvent], 2, around=False)  # get the changing page events
        initialSubgoals = self.subgoalsSet[:nbSubgoalsSetInitially[self.study]]    # get the list of the 2/3 subgoals initially set
        #print "InitialSubgoals: " + str(initialSubgoals)

        # get the number of pages relevant to each of the seven subgoals
        nbRelevantPagesForSubgoals = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0}
        for sgid, sgpagerow in enumerate(matPageSubgoal):
            nbRelevantPagesForSubgoals[sgid+1] = sum([1 if x>0 else 0 for x in sgpagerow])
        #print "NbRelPagePerSG: " + str(nbRelevantPagesForSubgoals)

        # get the total number of relevant pages associated to these subgoals initially set
        nbRelevantPagesForInitialSubgoals = [0]*nbPagesInSystem[self.study]
        for sgid in initialSubgoals:
            #print str(sgid) + "\t" + str(matPageSubgoal[sgid-1])
            nbRelevantPagesForInitialSubgoals = map(lambda x,y: x+y, nbRelevantPagesForInitialSubgoals, matPageSubgoal[sgid-1])    # add the line for this subgoal
        nbRelevantPagesForInitialSubgoals = sum([1 if x>0 else 0 for x in nbRelevantPagesForInitialSubgoals])
        #print "\t" + str(nbRelevantPagesForInitialSubgoals)

        alreadyVisitedPagesWithActiveSG = []
        alreadyVisitedAnytime = []

        for evt in evtslist:
            activeSubgoalId = self.getSubgoalWhenEvent(logger, evt)        # get the current subgoal

            # ************************ alreadyVisitedPages shouldn't be there at this point
            if (evt.timeSpentWithContent >= datetime.timedelta(seconds=15) and evt.pageIdx not in alreadyVisitedAnytime):   # if the page has been viewed for more than 15s
                alreadyVisitedAnytime.append(evt.pageIdx)   # add the page to the list of already visited pages

                for sgid in range(7):   # save it as read for any subgoal it's related to
                    self.relevancePageReadSubgoalsAnytime[sgid+1].append(1 if matPageSubgoal[sgid][int(evt.pageIdx)] > 0 else 0)
                relevantToInitSg = False

                for sgid in initialSubgoals:    # for the initial subgoals, count it as relevant if it's relevant to at least one of them
                    if matPageSubgoal[sgid-1][int(evt.pageIdx)] > 0:
                        self.relevancePageReadInitialSubgoalsAnytime.append(1)
                        relevantToInitSg = True
                        break
                if not relevantToInitSg:
                    self.relevancePageReadInitialSubgoalsAnytime.append(0)
                #print self.relevancePageReadInitialSubgoalsAnytime

            if (activeSubgoalId > 0 and evt.pageIdx not in alreadyVisitedPagesWithActiveSG): # if there is an active subgoal at this moment
                alreadyVisitedPagesWithActiveSG.append(evt.pageIdx) # add the page to the list of already visited pages

                try:
                    sgrelevance = matPageSubgoal[activeSubgoalId - 1][int(evt.pageIdx)]    # get the relevance of the current subgoal
                except IndexError:
                    self.logger.error("Unknown subgoal " + str(activeSubgoalId))
                    raise
                self.relevancePageVisitSubgoalsWhenActive[activeSubgoalId].append(1 if sgrelevance > 0 else 0)     # save the relevance of the current page for the current subgoal

                if (evt.timeSpentWithContent >= datetime.timedelta(seconds=15)):   # if the page has been viewed for more than 15s
                    self.relevancePageReadSubgoalsWhenActive[activeSubgoalId].append(1 if sgrelevance > 0 else 0)

                    if (activeSubgoalId in initialSubgoals):    # if the currently active subgoal is one of the initial ones
                        #print "L" + evt.pageIdx
                        sgrelevance = []
                        for initialSg in initialSubgoals:     # check if the page is relevant for at least one of those
                            sgrelevance.append(matPageSubgoal[initialSg - 1][int(evt.pageIdx)])
                        self.relevancePageReadInitialSubgoalsWhenActive.append(1 if max(sgrelevance)!=0 else 0) # add 1 if the maximum relevance to any of the originally set subgoals is at least 0.5
                    #else:
                        #print "S or VinP"

        #cptrel = 0
        #for page in self.relevancePageReadInitialSubgoalsWhenActive:
        #    if page > 0:
        #        cptrel += 1
        #self.ratioPagesVisitedRelevantToInitialSubgoals = float(cptrel) / len(self.relevancePageReadInitialSubgoalsWhenActive)
        try:
            self.ratioPagesRelevantToAnyInitialSubgoalsReadAnytime = float(self.relevancePageReadInitialSubgoalsAnytime.count(1)) / float(nbRelevantPagesForInitialSubgoals)
            self.ratioPagesRelevantToAnyInitialSubgoalsReadWhenActive = float(self.relevancePageReadInitialSubgoalsWhenActive.count(1)) / float(nbRelevantPagesForInitialSubgoals)
            self.ratioPagesIrrelevantToAnyInitialSubgoalsReadWhenActive = float(self.relevancePageReadInitialSubgoalsWhenActive.count(0)) / float(nbPagesInSystem[self.study] - nbRelevantPagesForInitialSubgoals)
        except ZeroDivisionError:
            self.ratioPagesRelevantToAnyInitialSubgoalsReadAnytime = "N/A"
            self.ratioPagesRelevantToAnyInitialSubgoalsReadWhenActive = "N/A"
            self.ratioPagesIrrelevantToAnyInitialSubgoalsReadWhenActive = "N/A"

        for sgid in initialSubgoals:
            try:
                self.ratioPagesRelevantToInitialSubgoalsVisitActive.append(sum(self.relevancePageVisitSubgoalsWhenActive[sgid]) / float(nbRelevantPagesForSubgoals[sgid]))
                self.ratioPagesRelevantToInitialSubgoalsReadAnytime.append(sum(self.relevancePageReadSubgoalsAnytime[sgid]) / float(nbRelevantPagesForSubgoals[sgid]))
                self.ratioPagesRelevantToInitialSubgoalsReadActive.append(sum(self.relevancePageReadSubgoalsWhenActive[sgid]) / float(nbRelevantPagesForSubgoals[sgid]))
            except ZeroDivisionError:
                self.ratioPagesRelevantToInitialSubgoalsVisitActive.append("N/A")
                self.ratioPagesRelevantToInitialSubgoalsReadAnytime.append("N/A")
                self.ratioPagesRelevantToInitialSubgoalsReadActive.append("N/A")
#        print self.ratioPagesRelevantToAnyInitialSubgoalsReadAnytime
#        print self.ratioPagesRelevantToAnyInitialSubgoalsReadWhenActive
#        print self.ratioPagesIrrelevantToAnyInitialSubgoalsReadWhenActive
#        print self.ratioPagesRelevantToInitialSubgoalsVisitActive
#        print self.ratioPagesRelevantToInitialSubgoalsReadAnytime
#        print self.ratioPagesRelevantToInitialSubgoalsReadActive



    def appendDay2Data(self, logger, ID, name, experimenter, otherdata, logEvents, offset):
        """Add day 2 data for a subject who had already been registered for his day 1"""
        # double check the name
        if not ((name.lower() in self.name.lower()) or (self.name.lower() in name.lower())):
            partNotIn = False
            for namepart in name.split(" "):    # deal with reversed names
                if not namepart.lower() in self.name.lower():
                    partNotIn = True
            if (self.ID not in MTSubject.checkedIDsForNameDifferenceBetweenDays):
                if partNotIn:
                    logger.warning("Possible error with subject " + ID + ", name is different for Day 1 and Day 2")
        self.experimenters[1] = experimenter
        self.group = otherdata[0+offset]

        if otherdata[1+offset] == "0":
            if (self.thinkaloud):
                logger.warning("Think aloud changed between 2 days")
            self.thinkaloud = False
        else:
            if (not self.thinkaloud):
                logger.warning("Think aloud changed between 2 days")
            self.thinkaloud = True

        #: the filename for day 2 log
        self.day2File = otherdata[2+offset]
        #: the list of MTEvent objects in the day 2
        self.day2Events = logEvents

        self.countSRLEvents() # count the SRL Events

    def appendPageData(self, logger, pageData):
        """Add a set of data related to the page views by the subject, with the form """
        self.pageData = pageData


#    @staticmethod
#    def getSummaryRowTitles(subjectData=False, experimentData=False, pageData=False, eventsData=False, SRLData=False):
#        """Build a list of titles for a chosen set of information about the subject"""
#        row = ["ID", "Group"]
#        if subjectData:
#            row.extend(["Name", "Gender", "Age", "Ethnicity", "Education", "GPA", "Major", "School", "#Courses"])
#        if experimentData:
#            row.extend(["Experimenter 1", "Experimenter 2", "Day1 log file", "Day2 log file"])
#        if pageData:
#            row.extend(["Page", "Start time"])#, "Time spent (s)"])
#        if SRLData:
#            row.extend(["PLAN","SUMM","TN","MPTG","RR","COIS","PKA","JOL","FOK","CE","INF","DEPENDS","Unknown"]) #(self.SRL.keys())
#        return row

    def getScoreOnQuestion(self, logger, test, questionId):
        """Return the score associated to a question in the pretest or post-test
        @param test the name of the test to consider (can be "pre" or "post")
        @param questionId a number corresponding to the index of the question in the test
        """
        if test not in ["pre", "post"]:
            logger.error("getScoreOnQuestion: Unknown test parameter value: " + str(test) + " (only 'pre' and 'post' are acceptable values)")
        if not isinstance(questionId, int):
            logger.error("getScoreOnQuestion: questionId parameter value: " + str(questionId) + "(needs to be an integer)")
        return self.testsIndividualQuestionsScore[0 if test == "pre" else 1][questionId]


    def getSummaryRowList(self, logger, dataTypes, prevrow, title=False):   #subjectData=False, experimentData=False, pageData=False, eventsData=False, SRLData=False):
        """Build a list made of a chosen set of information about the subject"""
        row = prevrow
        if len(dataTypes) == 0:
            return row      # end of recursion
        else:
            dataType = dataTypes[0]
        if dataType == "ID":
            if title:
                row.extend(["ID", "Group"])
            else:
                row.extend([self.ID, self.group])
        elif dataType == "subject":
            if title:
                row.extend(["Name", "Gender", "Age", "Ethnicity", "Education", "GPA", "Major", "School", "Courses", "#Courses"])
            else:
                row.extend([self.name, self.gender, self.age, self.ethnicity, self.education, self.GPA, self.major, self.school, self.courses, self.nbCourses])
        elif dataType == "experiment":
            if title:
                row.extend(["Experimenter Day1", "Experimenter Day2", "File Day1", "File Day2"])
            else:
                row.extend([self.experimenters[0], self.experimenters[1], self.day1File, self.day2File])
        elif dataType == "tests":

            if title:
                row.extend(["PreTest version", "PostTest version",
                            "PreTest Raw Score", "PreTest Raw Score ratio",
                            "PostTest Raw Score", "PostTest Raw Score ratio",
                            "Improvement for Raw Score", "Proportional Learning Gain for Raw Score", "Proportional Learning Gain (ignoring \"losses\") for Raw Score",

                            "PreTest Filtered Score", "Max PreTest Filtered Score", "PreTest Filtered Score ratio",
                            "PostTest Filtered Score", "Max PostTest Filtered Score", "PostTest Filtered Score ratio",
                            "Improvement for Filtered Score", "Proportional Learning Gain for Filtered Score", "Proportional Learning Gain (ignoreing \"losses\") for Filtered Score",

                            "PreTest Score Relative Pages Opened", "Max PreTest Score Relative Pages Opened", "PreTest Score Relative Pages Opened ratio",
                            "PostTest Score Relative Pages Opened", "Max PostTest Score Relative Pages Opened", "PostTest Score Relative Pages Opened ratio",
                            "Improvement for Relative Score Pages Opened", "Proportional Learning Gain for Relative Score Pages Opened", "Proportional Learning Gain (ignoring \"losses\") for Relative Score Pages Opened",

                            "PreTest Score Relative Pages Read 15s+", "Max PreTest Score Relative Pages Read 15s+", "PreTest Score Relative Pages Read 15s+ ratio",
                            "PostTest Score Relative Pages Read 15s+", "Max PostTest Score Relative Pages Read 15s+", "PostTest Score Relative Pages Read 15s+ ratio",
                            "Improvement for Relative Pages Read 15s+", "Proportional Learning Gain for Relative Pages Read 15s+", "Proportional Learning Gain (ignoring \"losses\") for Relative Score Pages Read 15s+"
                            ])
                for i in range(self.nbSubgoalsSetInitially):
                    row.extend([
                            "PreTest Score Relative SG " + str(i+1) +" initially set", "Max PreTest Score Relative SG " + str(i+1) +" initially set", "PreTest Score Relative SG " + str(i+1) +" initially set",
                            "PostTest Score Relative SG " + str(i+1) +" initially set", "Max PostTest Score Relative SG " + str(i+1) +" initially set", "PostTest Score Relative SG " + str(i+1) +" initially set",
                            "Improvement for Relative SG " + str(i+1) +" initially set", "Proportional Learning Gain for Relative SG " + str(i+1) +" initially set", "Proportional Learning Gain (ignoring \"losses\") for Relative SG " + str(i+1) +" initially set"
                                ])
                for i in range(self.nbSubgoalsSetInitially):
                    row.extend([
                            "PreTest Score Relative SG " + str(i+1) +" initially set, filtering out questions questions sig. better in post than pre", "Max PreTest Score Relative SG " + str(i+1) +" initially set, filtering out questions questions sig. better in post than pre", "PreTest Score Relative SG " + str(i+1) +" initially set, filtering out questions questions sig. better in post than pre",
                            "PostTest Score Relative SG " + str(i+1) +" initially set, filtering out questions questions sig. better in post than pre", "Max PostTest Score Relative SG " + str(i+1) +" initially set, filtering out questions questions sig. better in post than pre", "PostTest Score Relative SG " + str(i+1) +" initially set, filtering out questions questions sig. better in post than pre",
                            "Improvement for Relative SG " + str(i+1) +" initially set, filtering out questions questions sig. better in post than pre", "Proportional Learning Gain for Relative SG " + str(i+1) +" initially set, filtering out questions questions sig. better in post than pre", "Proportional Learning Gain (ignoring \"losses\") for Relative SG " + str(i+1) +" initially set, filtering out questions questions sig. better in post than pre"
                                ])
                row.extend([
                            "PreTest Score Relative all SG initially set", "Max PreTest Score Relative all SG initially set", "PreTest Score Relative all SG initially set",
                            "PostTest Score Relative all SG initially set", "Max PostTest Score Relative all SG initially set", "PostTest Score Relative all SG initially set",
                            "Improvement for Relative all SG initially set", "Proportional Learning Gain for Relative all SG initially set", "Proportional Learning Gain (ignoring \"losses\") for Relative all SG initially set",

                            "PreTest Score Relative all SG initially set, filtering out questions questions sig. better in post than pre", "Max PreTest Score Relative all SG initially set, filtering out questions questions sig. better in post than pre", "PreTest Score Relative all SG initially set, filtering out questions questions sig. better in post than pre",
                            "PostTest Score Relative all SG initially set, filtering out questions questions sig. better in post than pre", "Max PostTest Score Relative all SG initially set, filtering out questions questions sig. better in post than pre", "PostTest Score Relative all SG initially set, filtering out questions questions sig. better in post than pre",
                            "Improvement for Relative all SG initially set, filtering out questions questions sig. better in post than pre", "Proportional Learning Gain for Relative all SG initially set, filtering out questions questions sig. better in post than pre", "Proportional Learning Gain (ignoring \"losses\") for Relative all SG initially set, filtering out questions questions sig. better in post than pre",

                            "PreTest Score Relative SG set", "Max PreTest Score Relative SG set", "PreTest Score Relative SG set ratio",
                            "PostTest Score Relative SG set", "Max PostTest Score Relative SG set", "PostTest Score Relative SG set ratio",
                            "Improvement for Relative SG set", "Proportional Learning Gain for Relative SG set", "Proportional Learning Gain (ignoring \"losses\") for Relative SG set",

                            "PreTest Score Relative SG actively pursued", "Max PreTest Score Relative SG actively pursued", "PreTest Score Relative SG actively pursued ratio",
                            "PostTest Score Relative SG actively pursued", "Max PostTest Score Relative SG actively pursued", "PostTest Score Relative SG actively pursued ratio",
                            "Improvement for Relative SG actively pursued", "Proportional Learning Gain for Relative SG actively pursued", "Proportional Learning Gain (ignoring \"losses\") for Relative SG actively pursued"
                            ])
            else:
                #row.extend([self.preTestScore, self.postTestScore, self.postTestScoreRelativeOpenedPages, self.postTestMaxScoreOpenedPages, self.postTestScoreRelativeReadLongPages, self.postTestMaxScoreReadLongPages, self.postTestScoreRelativeSubgoalPursued, self.postTestMaxScoreSubgoalPursued])
                try:
                    row.extend([self.testsVersion[0], self.testsVersion[1],
                            self.testsScoreRaw[0], float(self.testsScoreRaw[0])/25,
                            self.testsScoreRaw[1], float(self.testsScoreRaw[1])/25,
                            self.testsScoreRaw[1] - self.testsScoreRaw[0], self.calculateLearningGain(float(self.testsScoreRaw[0])/25, float(self.testsScoreRaw[1])/25), self.calculateLearningGainWithoutLosses(float(self.testsScoreRaw[0])/25, float(self.testsScoreRaw[1])/25),

                            self.testsScoreRawFiltered[0], self.testsMaxScoreRawFiltered[0], float(self.testsScoreRawFiltered[0])/self.testsMaxScoreRawFiltered[0],
                            self.testsScoreRawFiltered[1], self.testsMaxScoreRawFiltered[1], float(self.testsScoreRawFiltered[1])/self.testsMaxScoreRawFiltered[1],
                            "N/A", self.calculateLearningGain(float(self.testsScoreRawFiltered[0])/self.testsMaxScoreRawFiltered[0], float(self.testsScoreRawFiltered[1])/self.testsMaxScoreRawFiltered[1]), self.calculateLearningGainWithoutLosses(float(self.testsScoreRawFiltered[0])/self.testsMaxScoreRawFiltered[0], float(self.testsScoreRawFiltered[1])/self.testsMaxScoreRawFiltered[1]),

                            self.testsScoreRelativeOpenedPages[0], self.testsMaxScoreOpenedPages[0], float(self.testsScoreRelativeOpenedPages[0])/self.testsMaxScoreOpenedPages[0],
                            self.testsScoreRelativeOpenedPages[1], self.testsMaxScoreOpenedPages[1], float(self.testsScoreRelativeOpenedPages[1])/self.testsMaxScoreOpenedPages[1],
                            self.testsScoreRelativeOpenedPages[1] - self.testsScoreRelativeOpenedPages[0], self.calculateLearningGain(float(self.testsScoreRelativeOpenedPages[0])/self.testsMaxScoreOpenedPages[0], float(self.testsScoreRelativeOpenedPages[1])/self.testsMaxScoreOpenedPages[1]), self.calculateLearningGainWithoutLosses(float(self.testsScoreRelativeOpenedPages[0])/self.testsMaxScoreOpenedPages[0], float(self.testsScoreRelativeOpenedPages[1])/self.testsMaxScoreOpenedPages[1]),

                            self.testsScoreRelativeReadLongPages[0], self.testsMaxScoreReadLongPages[0], float(self.testsScoreRelativeReadLongPages[0])/self.testsMaxScoreReadLongPages[0],
                            self.testsScoreRelativeReadLongPages[1], self.testsMaxScoreReadLongPages[1], float(self.testsScoreRelativeReadLongPages[1])/self.testsMaxScoreReadLongPages[1],
                            self.testsScoreRelativeReadLongPages[1] - self.testsScoreRelativeReadLongPages[0], self.calculateLearningGain(float(self.testsScoreRelativeReadLongPages[0])/self.testsMaxScoreReadLongPages[0], float(self.testsScoreRelativeReadLongPages[1])/self.testsMaxScoreReadLongPages[1]), self.calculateLearningGainWithoutLosses(float(self.testsScoreRelativeReadLongPages[0])/self.testsMaxScoreReadLongPages[0], float(self.testsScoreRelativeReadLongPages[1])/self.testsMaxScoreReadLongPages[1])
                            ])
                except ZeroDivisionError:
                    row.extend([self.testsVersion[0], self.testsVersion[1],
                                self.testsScoreRaw[0], float(self.testsScoreRaw[0])/25,
                                self.testsScoreRaw[1], float(self.testsScoreRaw[1])/25,
                                self.testsScoreRaw[1] - self.testsScoreRaw[0], self.calculateLearningGain(float(self.testsScoreRaw[0])/25, float(self.testsScoreRaw[1])/25), self.calculateLearningGainWithoutLosses(float(self.testsScoreRaw[0])/25, float(self.testsScoreRaw[1])/25),

                                self.testsScoreRawFiltered[0], self.testsMaxScoreRawFiltered[0], "N/A",
                                self.testsScoreRawFiltered[1], self.testsMaxScoreRawFiltered[1], "N/A",
                                "N/A", "N/A", "N/A",

                                self.testsScoreRelativeOpenedPages[0], self.testsMaxScoreOpenedPages[0], "N/A",
                                self.testsScoreRelativeOpenedPages[1], self.testsMaxScoreOpenedPages[1], "N/A",
                                self.testsScoreRelativeOpenedPages[1] - self.testsScoreRelativeOpenedPages[0], "N/A", "N/A",

                                self.testsScoreRelativeReadLongPages[0], self.testsMaxScoreReadLongPages[0], "N/A",
                                self.testsScoreRelativeReadLongPages[1], self.testsMaxScoreReadLongPages[1], "N/A",
                                self.testsScoreRelativeReadLongPages[1] - self.testsScoreRelativeReadLongPages[0], "N/A", "N/A" ])

                for i in range(self.nbSubgoalsSetInitially):
                    try:
                        row.extend([
                            self.testsScoreRelativeSubgoalSetInitially[0][i], self.testsMaxScoreSubgoalSetInitially[0][i], float(self.testsScoreRelativeSubgoalSetInitially[0][i])/self.testsMaxScoreSubgoalSetInitially[0][i],
                            self.testsScoreRelativeSubgoalSetInitially[1][i], self.testsMaxScoreSubgoalSetInitially[1][i], float(self.testsScoreRelativeSubgoalSetInitially[1][i])/self.testsMaxScoreSubgoalSetInitially[1][i],
                            self.testsScoreRelativeSubgoalSetInitially[1][i] - self.testsScoreRelativeSubgoalSetInitially[0][i], self.calculateLearningGain(float(self.testsScoreRelativeSubgoalSetInitially[0][i])/self.testsMaxScoreSubgoalSetInitially[0][i], float(self.testsScoreRelativeSubgoalSetInitially[1][i])/self.testsMaxScoreSubgoalSetInitially[1][i]), self.calculateLearningGainWithoutLosses(float(self.testsScoreRelativeSubgoalSetInitially[0][i])/self.testsMaxScoreSubgoalSetInitially[0][i], float(self.testsScoreRelativeSubgoalSetInitially[1][i])/self.testsMaxScoreSubgoalSetInitially[1][i])
                            ])
                    except ZeroDivisionError:   # when there was a system crash at the beginning that prevented to set 3 subgoals
                        row.extend(["N/A"]*9)

                for i in range(self.nbSubgoalsSetInitially):
                    try:
                        row.extend([
                            self.testsScoreRelativeSubgoalSetInitiallyFiltered[0][i], self.testsMaxScoreSubgoalSetInitiallyFiltered[0][i], float(self.testsScoreRelativeSubgoalSetInitiallyFiltered[0][i])/self.testsMaxScoreSubgoalSetInitiallyFiltered[0][i],
                            self.testsScoreRelativeSubgoalSetInitiallyFiltered[1][i], self.testsMaxScoreSubgoalSetInitiallyFiltered[1][i], float(self.testsScoreRelativeSubgoalSetInitiallyFiltered[1][i])/self.testsMaxScoreSubgoalSetInitiallyFiltered[1][i],
                            self.testsScoreRelativeSubgoalSetInitiallyFiltered[1][i] - self.testsScoreRelativeSubgoalSetInitiallyFiltered[0][i], self.calculateLearningGain(float(self.testsScoreRelativeSubgoalSetInitiallyFiltered[0][i])/self.testsMaxScoreSubgoalSetInitiallyFiltered[0][i], float(self.testsScoreRelativeSubgoalSetInitiallyFiltered[1][i])/self.testsMaxScoreSubgoalSetInitiallyFiltered[1][i]), self.calculateLearningGainWithoutLosses(float(self.testsScoreRelativeSubgoalSetInitiallyFiltered[0][i])/self.testsMaxScoreSubgoalSetInitiallyFiltered[0][i], float(self.testsScoreRelativeSubgoalSetInitiallyFiltered[1][i])/self.testsMaxScoreSubgoalSetInitiallyFiltered[1][i])
                            ])
                    except ZeroDivisionError:   # when there was a system crash at the beginning that prevented to set 3 subgoals
                        row.extend(["N/A"]*9)

                try:
                    row.extend([
                            # With overlap of SG (i.e. the max score can be superior to 25 and question count "double" if 2 initial SGs were relative to it)
                            #sum(self.testsScoreRelativeSubgoalSetInitially[0]), sum(self.testsMaxScoreSubgoalSetInitially[0]), float(sum(self.testsScoreRelativeSubgoalSetInitially[0]))/sum(self.testsMaxScoreSubgoalSetInitially[0]),
                            #sum(self.testsScoreRelativeSubgoalSetInitially[1]), sum(self.testsMaxScoreSubgoalSetInitially[1]), float(sum(self.testsScoreRelativeSubgoalSetInitially[1]))/sum(self.testsMaxScoreSubgoalSetInitially[1]),
                            #sum(self.testsScoreRelativeSubgoalSetInitially[1]) - sum(self.testsScoreRelativeSubgoalSetInitially[0]), MTLogAnalyzer.calculateLearningGain(float(sum(self.testsScoreRelativeSubgoalSetInitially[0]))/sum(self.testsMaxScoreSubgoalSetInitially[0]), float(sum(self.testsScoreRelativeSubgoalSetInitially[1]))/sum(self.testsMaxScoreSubgoalSetInitially[1])), MTLogAnalyzer.calculateLearningGainWithoutLosses(float(sum(self.testsScoreRelativeSubgoalSetInitially[0]))/sum(self.testsMaxScoreSubgoalSetInitially[0]), float(sum(self.testsScoreRelativeSubgoalSetInitially[1]))/sum(self.testsMaxScoreSubgoalSetInitially[1])),

                            # Without overlap of SG (i.e. each question is worth one point, regardless of how many initial subgoals were relative to it, as long as at least one was
                            self.testsScoreRelativeAllSubgoalsSetInitially[0], self.testsMaxScoreAllSubgoalsSetInitially[0], float(self.testsScoreRelativeAllSubgoalsSetInitially[0])/self.testsMaxScoreAllSubgoalsSetInitially[0],
                            self.testsScoreRelativeAllSubgoalsSetInitially[1], self.testsMaxScoreAllSubgoalsSetInitially[1], float(self.testsScoreRelativeAllSubgoalsSetInitially[1])/self.testsMaxScoreAllSubgoalsSetInitially[1],
                            self.testsScoreRelativeAllSubgoalsSetInitially[1] - self.testsScoreRelativeAllSubgoalsSetInitially[0], self.calculateLearningGain(float(self.testsScoreRelativeAllSubgoalsSetInitially[0])/self.testsMaxScoreAllSubgoalsSetInitially[0], float(self.testsScoreRelativeAllSubgoalsSetInitially[1])/self.testsMaxScoreAllSubgoalsSetInitially[1]), self.calculateLearningGainWithoutLosses(float(self.testsScoreRelativeAllSubgoalsSetInitially[0])/self.testsMaxScoreAllSubgoalsSetInitially[0], float(self.testsScoreRelativeAllSubgoalsSetInitially[1])/self.testsMaxScoreAllSubgoalsSetInitially[1]),

                            self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[0], self.testsMaxScoreAllSubgoalsSetInitiallyFiltered[0], float(self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[0])/self.testsMaxScoreAllSubgoalsSetInitiallyFiltered[0],
                            self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[1], self.testsMaxScoreAllSubgoalsSetInitiallyFiltered[1], float(self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[1])/self.testsMaxScoreAllSubgoalsSetInitiallyFiltered[1],
                            self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[1] - self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[0], self.calculateLearningGain(float(self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[0])/self.testsMaxScoreAllSubgoalsSetInitiallyFiltered[0], float(self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[1])/self.testsMaxScoreAllSubgoalsSetInitiallyFiltered[1]), self.calculateLearningGainWithoutLosses(float(self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[0])/self.testsMaxScoreAllSubgoalsSetInitiallyFiltered[0], float(self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[1])/self.testsMaxScoreAllSubgoalsSetInitiallyFiltered[1]),

                            self.testsScoreRelativeSubgoalSet[0], self.testsMaxScoreSubgoalSet[0], float(self.testsScoreRelativeSubgoalSet[0])/self.testsMaxScoreSubgoalSet[0],
                            self.testsScoreRelativeSubgoalSet[1], self.testsMaxScoreSubgoalSet[1], float(self.testsScoreRelativeSubgoalSet[1])/self.testsMaxScoreSubgoalSet[1],
                            self.testsScoreRelativeSubgoalSet[1] - self.testsScoreRelativeSubgoalSet[0], self.calculateLearningGain(float(self.testsScoreRelativeSubgoalSet[0])/self.testsMaxScoreSubgoalSet[0], float(self.testsScoreRelativeSubgoalSet[1])/self.testsMaxScoreSubgoalSet[1]), self.calculateLearningGainWithoutLosses(float(self.testsScoreRelativeSubgoalSet[0])/self.testsMaxScoreSubgoalSet[0], float(self.testsScoreRelativeSubgoalSet[1])/self.testsMaxScoreSubgoalSet[1]),

                            self.testsScoreRelativeSubgoalPursued[0], self.testsMaxScoreSubgoalPursued[0], float(self.testsScoreRelativeSubgoalPursued[0])/self.testsMaxScoreSubgoalPursued[0],
                            self.testsScoreRelativeSubgoalPursued[1], self.testsMaxScoreSubgoalPursued[1], float(self.testsScoreRelativeSubgoalPursued[1])/self.testsMaxScoreSubgoalPursued[1],
                            self.testsScoreRelativeSubgoalPursued[1] - self.testsScoreRelativeSubgoalPursued[0], self.calculateLearningGain(float(self.testsScoreRelativeSubgoalPursued[0])/self.testsMaxScoreSubgoalPursued[0], float(self.testsScoreRelativeSubgoalPursued[1])/self.testsMaxScoreSubgoalPursued[1]), self.calculateLearningGainWithoutLosses(float(self.testsScoreRelativeSubgoalPursued[0])/self.testsMaxScoreSubgoalPursued[0], float(self.testsScoreRelativeSubgoalPursued[1])/self.testsMaxScoreSubgoalPursued[1])
                           ])
                except ZeroDivisionError:
                    row.extend([
                            # With overlap of SG (i.e. the max score can be superior to 25 and question count "double" if 2 initial SGs were relative to it)
                            #sum(self.testsScoreRelativeSubgoalSetInitially[0]), sum(self.testsMaxScoreSubgoalSetInitially[0]), float(sum(self.testsScoreRelativeSubgoalSetInitially[0]))/sum(self.testsMaxScoreSubgoalSetInitially[0]),
                            #sum(self.testsScoreRelativeSubgoalSetInitially[1]), sum(self.testsMaxScoreSubgoalSetInitially[1]), float(sum(self.testsScoreRelativeSubgoalSetInitially[1]))/sum(self.testsMaxScoreSubgoalSetInitially[1]),
                            #sum(self.testsScoreRelativeSubgoalSetInitially[1]) - sum(self.testsScoreRelativeSubgoalSetInitially[0]), MTLogAnalyzer.calculateLearningGain(float(sum(self.testsScoreRelativeSubgoalSetInitially[0]))/sum(self.testsMaxScoreSubgoalSetInitially[0]), float(sum(self.testsScoreRelativeSubgoalSetInitially[1]))/sum(self.testsMaxScoreSubgoalSetInitially[1])), MTLogAnalyzer.calculateLearningGainWithoutLosses(float(sum(self.testsScoreRelativeSubgoalSetInitially[0]))/sum(self.testsMaxScoreSubgoalSetInitially[0]), float(sum(self.testsScoreRelativeSubgoalSetInitially[1]))/sum(self.testsMaxScoreSubgoalSetInitially[1])),

                            # Without overlap of SG (i.e. each question is worth one point, regardless of how many initial subgoals were relative to it, as long as at least one was
                            self.testsScoreRelativeAllSubgoalsSetInitially[0], self.testsMaxScoreAllSubgoalsSetInitially[0], "N/A",
                            self.testsScoreRelativeAllSubgoalsSetInitially[1], self.testsMaxScoreAllSubgoalsSetInitially[1], "N/A",
                            self.testsScoreRelativeAllSubgoalsSetInitially[1] - self.testsScoreRelativeAllSubgoalsSetInitially[0], "N/A", "N/A",

                            self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[0], self.testsMaxScoreAllSubgoalsSetInitiallyFiltered[0], "N/A",
                            self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[1], self.testsMaxScoreAllSubgoalsSetInitiallyFiltered[1], "N/A",
                            self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[1] - self.testsScoreRelativeAllSubgoalsSetInitiallyFiltered[0], "N/A", "N/A",

                            self.testsScoreRelativeSubgoalSet[0], self.testsMaxScoreSubgoalSet[0],"N/A",
                            self.testsScoreRelativeSubgoalSet[1], self.testsMaxScoreSubgoalSet[1], "N/A",
                            self.testsScoreRelativeSubgoalSet[1] - self.testsScoreRelativeSubgoalSet[0], "N/A","N/A",

                            self.testsScoreRelativeSubgoalPursued[0], self.testsMaxScoreSubgoalPursued[0], "N/A",
                            self.testsScoreRelativeSubgoalPursued[1], self.testsMaxScoreSubgoalPursued[1], "N/A",
                            self.testsScoreRelativeSubgoalPursued[1] - self.testsScoreRelativeSubgoalPursued[0], "N/A","N/A"
                           ])

        elif dataType == "times":
            if title:
                row.extend(["Session duration", "Reading duration"])
            else:
                row.extend([self.sessionDuration.seconds, self.readingDuration.seconds])
        elif dataType == "subgoals":
            if title:
                row.extend(["#Subgoals validated", "#Subgoals attempted", "Worked without subgoal", "#Subgoals changes"])
            else:
                row.extend([self.nbSubgoalsValidated, self.nbSubgoalsAttempted, self.workedWithoutSubgoals, self.nbSubgoalChanges])
        elif dataType == "quizzesSubgoal":
            if title:
                row.extend(["#Subgoal Quizzes", "Subgoal Quizzes Mean Score", "Subgoal Quizzes Weighted Mean Score", "Subgoal Quizzes Mean First Score", "Subgoal Quizzes Weighted Mean First Score"])
                for i in range(self.nbSubgoalsSetInitially):
                    row.append("Mean score on SG" + str(i+1) + " quiz")
            else:
                row.extend([self.quizSubgoalNb, self.quizSubgoalMeanScore, self.quizSubgoalWeightedMeanScore, self.quizSubgoalMeanScoreFirst, self.quizSubgoalWeightedMeanScoreFirst])
                for i in range(self.nbSubgoalsSetInitially):
                    try:
                        row.append(sum(self.quizSubgoalScore[self.subgoalsSet[i]]) / float(len(self.quizSubgoalScore[self.subgoalsSet[i]])))
                    except ZeroDivisionError:
                        row.append("N/A")
        elif dataType == "quizzesPage":
            if title:
                row.extend(["#Page Quizzes", "Page Quizzes Mean Score", "Page Quizzes Weighted Mean Score", "Page Quizzes Mean First Score", "Page Quizzes Weighted Mean First Score"])
                for i in range(self.nbSubgoalsSetInitially):
                    row.append("Mean score on quizzes on pages relevant to SG" + str(i+1) + " when SG" + str(i+1) + " was active")
                for i in range(self.nbSubgoalsSetInitially):
                    row.append("Mean score on quizzes on pages relevant to SG" + str(i+1) + " taken anytime in the session")
            else:
                row.extend([self.quizPageNb, self.quizPageMeanScore, self.quizPageWeightedMeanScore, self.quizPageMeanScoreFirst, self.quizPageWeightedMeanScoreFirst])
                for i in range(self.nbSubgoalsSetInitially):
                    try:
                        row.append(sum(self.quizPageScoreRelevantSubgoalWhenActive[self.subgoalsSet[i]]) / float(len(self.quizPageScoreRelevantSubgoalWhenActive[self.subgoalsSet[i]])))
                    except ZeroDivisionError:
                        row.append("N/A")
                for i in range(self.nbSubgoalsSetInitially):
                    try:
                        row.append(sum(self.quizPageScoreRelevantSubgoalAnytime[self.subgoalsSet[i]]) / float(len(self.quizPageScoreRelevantSubgoalAnytime[self.subgoalsSet[i]])))
                    except ZeroDivisionError:
                        row.append("N/A")
        elif dataType == "notes":
            if title:
                row.extend(["#Note Taking", "#Note Checking", "#Summaries added to notes","Note Taking Duration", "Note Checking Duration"])
            else:
                row.extend([self.nbNoteTaking, self.nbNoteChecking, self.nbNoteSummaryAdd, Utils.getSecondsFromDatetime(self.noteTakingDuration), Utils.getSecondsFromDatetime(self.noteCheckingDuration)])
        elif dataType == "pagesViewEvents":
            if title:
                row.extend(["Page Views..."])
            else:
                for page in self.pageData:
                    row.extend(page)
        elif dataType == "pagesRelInitSG":
                if title:
                    #row.extend(["RatioRelevantPagesToInitialSubgoalsVisitedMoreThan15sWhileWorkingOnThem", "RatioIrrelevantPagesToInitialSubgoalsVisitedMoreThan15sWhileWorkingOnThem"])
                    for sgid, _ in enumerate(self.ratioPagesRelevantToInitialSubgoalsReadActive):
                        row.append("RatioPagesRelevantToInitialSubgoal" + str(sgid+1) + "ReadWhenSubgoal" + str(sgid+1) + "Active")
                    for sgid, _ in enumerate(self.ratioPagesRelevantToInitialSubgoalsReadAnytime):
                        row.append("RatioPagesRelevantToInitialSubgoal" + str(sgid+1) + "ReadAtAnytime")
                else:
                    #row.extend([self.ratioPagesRelevantToAnyInitialSubgoalsReadWhenActive, self.ratioPagesIrrelevantToAnyInitialSubgoalsReadWhenActive])
                    row.extend(self.ratioPagesRelevantToInitialSubgoalsReadActive)
                    row.extend(self.ratioPagesRelevantToInitialSubgoalsReadAnytime)
        elif dataType == "allEvents":
            if title:
                row.append("All events...")
            else:
                for event in self.day1Events:
                    row.extend(event.getInfo(showAll=True))
                for event in self.day2Events:
                    row.extend(event.getInfo(showAll=True))
        elif dataType == "SRLEvents":
            for srl in ["PLAN", "SUMM", "TN", "MPTG", "RR", "COIS", "PKA", "JOL", "FOK", "CE", "INF", "DEPENDS", "Unknown"]:
                if title:
                    row.append("#"+srl)
                else:
                    row.append(self.SRL[srl])
            for sgid, sg in enumerate(self.subgoalsSet[:self.nbSubgoalsSetInitially]):
                if title:
                    row.append("Mean # of SRL processes per relevant page while on SG" + str(sgid))
                else:
                    cptSrl = 0
                    cptPage = 0
                    for page in self.SRLPagesRelevantSubgoalWhenActive[sg]:
                        cptPage += 1
                        cptSrl += self.SRLPagesRelevantSubgoalWhenActive[sg][page]
                    try:
                        row.append(cptSrl/float(cptPage))
                    except ZeroDivisionError:
                        row.append("N/A")
            for sgid, sg in enumerate(self.subgoalsSet[:self.nbSubgoalsSetInitially]):
                if title:
                    row.append("Mean # of SRL processes per relevant page to SG" + str(sgid) + " at anytime in the session (NB: some processes can end up being counted multiple times)")
                else:
                    cptSrl = 0
                    cptPage = 0
                    for page in self.SRLPagesRelevantSubgoalAnytime[sg]:
                        cptPage += 1
                        cptSrl += self.SRLPagesRelevantSubgoalAnytime[sg][page]
                    try:
                        row.append(cptSrl/float(cptPage))
                    except ZeroDivisionError:
                        row.append("N/A")

        #bondaria------
        elif  dataType == "Durations":
            if title:
                row.extend(["TotalTimeWithContent ", "TimePageRelSG", "TimePageIrrelSG", "ProportionTimeRelSGOverReading", "ProportionTimeIrrelSGOverReading",
                            "TotalTimeWithRelTextCntent", "TotalTimeWithRelFullContent", "TotalTimeWithIrrelTextContent", "TotalTimeWithIrrelFullContent",
                            "NoteTakingDuration", "NoteCheckingDuration",
                            "Number of subgoals set", "Total Time Spent On setting Subgoals", "Average Time Setting SG", "Duration of Reading Overall", "TimeSpentWithContentOverall",
                            "TimePaperNotes", "TimeINF", "TimePKA", "TimeSummary"])
            else:
                #convert timedelts to miliseconds
                def TimeDelta2Miliseconds(td):
                    return td.seconds * 1000 + td.microseconds/1000

                #row.extend([TimeDelta2Miliseconds(self.pagesTotalTimeSpentWithContent), TimeDelta2Miliseconds(self.readingDuration), TimeDelta2Miliseconds(self.pagesTotalTimeSpentRelevantSG), self.pagesTimeProportionSGRel,
                #            TimeDelta2Miliseconds(self.timeSpentWithContentNoImageRel), TimeDelta2Miliseconds(self.timeSpentWithContentImageRel), TimeDelta2Miliseconds(self.timeSpentWithContentNoImageIrrel), TimeDelta2Miliseconds(self.timeSpentWithContentImageIrrel),
                #            Utils.getMilliSecondsFromDatetime(self.noteTakingDuration), Utils.getMilliSecondsFromDatetime(self.noteCheckingDuration),
                #            self.NbSGTotal, TimeDelta2Miliseconds(self.SGTimeTotal), TimeDelta2Miliseconds(self.SGTimeAVG)
                #            ])

                row.extend([TimeDelta2Miliseconds(self.pagesTotalTimeSpentWithContent), TimeDelta2Miliseconds(self.pagesTotalTimeSpentRelevantSG), TimeDelta2Miliseconds(self.pagesTotalTimeSpentIrrelSG), self.pagesTimeProportionSGRel,self.pagesTimeProportionSGIrrel,
                            TimeDelta2Miliseconds(self.timeSpentWithContentNoImageRel), TimeDelta2Miliseconds(self.timeSpentWithContentImageRel), TimeDelta2Miliseconds(self.timeSpentWithContentNoImageIrrel), TimeDelta2Miliseconds(self.timeSpentWithContentImageIrrel),
                            Utils.getMilliSecondsFromDatetime(self.noteTakingDuration), Utils.getMilliSecondsFromDatetime(self.noteCheckingDuration),
                            self.NbSGTotal, self.SGTimeTotal.seconds, self.SGTimeAVG.seconds, TimeDelta2Miliseconds(self.sessionDuration), TimeDelta2Miliseconds(self.pageTotalTimeOverall),
                            TimeDelta2Miliseconds(self.DurationNoteTakenOnPaper),TimeDelta2Miliseconds(self.DurationUserTypingINF),TimeDelta2Miliseconds(self.DurationUserTypingPKA),TimeDelta2Miliseconds(self.DurationUserTypingSummary)
                            ])



                '''
        self.pagesTotalTimeSpentWithContent = datetime.timedelta(0,0,0)
        self.pagesTotalTimeSpentRelevantSG = datetime.timedelta(0,0,0)
        self.pagesTimeProportionSGRel = 0

        self.SGTimeTotal = datetime.timedelta(0,0,0)
        self.SGTimeAVG = datetime.timedelta(0,0,0)

        self.NbSGTotal = 0
        self.timeSpentWithContentImage = datetime.timedelta(0, 0, 0)
        self.timeSpentWithContentNoImage = datetime.timedelta(0, 0, 0)
        self.timeSpentWithContentImageRel = datetime.timedelta(0, 0, 0)
        self.timeSpentWithContentNoImageRel = datetime.timedelta(0, 0, 0)
        self.timeSpentWithContentImageIrrel = datetime.timedelta(0, 0, 0)
        self.timeSpentWithContentNoImageIrrel = datetime.timedelta(0, 0, 0)

                '''

        elif dataType == "ActionsFeatures":
            if title:
                row.extend(["DurationDay2", "DurationInteractionDay2", "DurationBrowsing", "TimeSpentWithContentOverall",
                            "TotalTimeWithContent ", "TimePageRelSG", "TimePageIrrelSG", "ProportionTimeRelSGOverReading", "ProportionTimeIrrelSGOverReading",
                            "TotalTimeWithRelTextContent", "TotalTimeWithRelFullContent", "TotalTimeWithIrrelTextContent", "TotalTimeWithIrrelFullContent",
                            "NumberSG", "TotalTimeSettingSG", "AverageTimeSettingSG",
                            "NoteTakingDuration", "NoteCheckingDuration", "NoteTakingNum", "NoteCheckingNum", "SummaryAddedNumber",
                            "TimePaperNotes", "TimeINF", "TimePKA", "TimeSummary",
                            "SGValidated", "SGAttempted", "FlagWorkedWithoutSubgoal", "SGChanged"
                            ])
                    #row.extend(["RatioRelevantPagesToInitialSubgoalsVisitedMoreThan15sWhileWorkingOnThem", "RatioIrrelevantPagesToInitialSubgoalsVisitedMoreThan15sWhileWorkingOnThem"])
                for sgid, _ in enumerate(self.ratioPagesRelevantToInitialSubgoalsReadActive):
                    row.append("RatioPagesRelevantToInitialSubgoal" + str(sgid+1) + "ReadWhenSubgoal" + str(sgid+1) + "Active")
                for sgid, _ in enumerate(self.ratioPagesRelevantToInitialSubgoalsReadAnytime):
                    row.append("RatioPagesRelevantToInitialSubgoal" + str(sgid+1) + "ReadAtAnytime")
            else:
                #convert timedelts to miliseconds
                def TimeDelta2Miliseconds(td):
                    return td.seconds * 1000 + td.microseconds/1000

                #row.extend([TimeDelta2Miliseconds(self.pagesTotalTimeSpentWithContent), TimeDelta2Miliseconds(self.readingDuration), TimeDelta2Miliseconds(self.pagesTotalTimeSpentRelevantSG), self.pagesTimeProportionSGRel,
                #            TimeDelta2Miliseconds(self.timeSpentWithContentNoImageRel), TimeDelta2Miliseconds(self.timeSpentWithContentImageRel), TimeDelta2Miliseconds(self.timeSpentWithContentNoImageIrrel), TimeDelta2Miliseconds(self.timeSpentWithContentImageIrrel),
                #            Utils.getMilliSecondsFromDatetime(self.noteTakingDuration), Utils.getMilliSecondsFromDatetime(self.noteCheckingDuration),
                #            self.NbSGTotal, TimeDelta2Miliseconds(self.SGTimeTotal), TimeDelta2Miliseconds(self.SGTimeAVG)
                #            ])

                row.extend([TimeDelta2Miliseconds(self.DurationDay2), TimeDelta2Miliseconds(self.DurationMTInteractionDay2), TimeDelta2Miliseconds(self.sessionDuration), TimeDelta2Miliseconds(self.pageTotalTimeOverall),
                            TimeDelta2Miliseconds(self.pagesTotalTimeSpentWithContent), TimeDelta2Miliseconds(self.pagesTotalTimeSpentRelevantSG), TimeDelta2Miliseconds(self.pagesTotalTimeSpentIrrelSG), self.pagesTimeProportionSGRel,self.pagesTimeProportionSGIrrel,
                            TimeDelta2Miliseconds(self.timeSpentWithContentNoImageRel), TimeDelta2Miliseconds(self.timeSpentWithContentImageRel), TimeDelta2Miliseconds(self.timeSpentWithContentNoImageIrrel), TimeDelta2Miliseconds(self.timeSpentWithContentImageIrrel),
                            self.NbSGTotal, self.SGTimeTotal.seconds, self.SGTimeAVG.seconds,
                            Utils.getMilliSecondsFromDatetime(self.noteTakingDuration), Utils.getMilliSecondsFromDatetime(self.noteCheckingDuration),self.nbNoteTaking, self.nbNoteChecking, self.nbNoteSummaryAdd,
                            TimeDelta2Miliseconds(self.DurationNoteTakenOnPaper),TimeDelta2Miliseconds(self.DurationUserTypingINF),TimeDelta2Miliseconds(self.DurationUserTypingPKA),TimeDelta2Miliseconds(self.DurationUserTypingSummary),
                            self.nbSubgoalsValidated, self.nbSubgoalsAttempted, self.workedWithoutSubgoals, self.nbSubgoalChanges
                            ])
                print( self.ID," Note Taking", self.noteTakingDuration)
                print( self.ID," Note Checking", self.noteCheckingDuration)
                #add number of pages relevant to sg
                row.extend(self.ratioPagesRelevantToInitialSubgoalsReadActive)
                row.extend(self.ratioPagesRelevantToInitialSubgoalsReadAnytime)
            #add features relevant to SRL
            for srl in ["PLAN", "SUMM", "TN", "MPTG", "RR", "COIS", "PKA", "JOL", "FOK", "CE", "INF"]:
                if title:
                    row.append("num"+srl)
                else:
                    row.append(self.SRL[srl])
            for sgid, sg in enumerate(self.subgoalsSet[:self.nbSubgoalsSetInitially]):
                if title:
                    row.append("AVGNumSRLperPagetoSG" + str(sgid)+"Active")
                else:
                    cptSrl = 0
                    cptPage = 0
                    for page in self.SRLPagesRelevantSubgoalWhenActive[sg]:
                        cptPage += 1
                        cptSrl += self.SRLPagesRelevantSubgoalWhenActive[sg][page]
                    try:
                        row.append(cptSrl/float(cptPage))
                    except ZeroDivisionError:
                        row.append("N/A")
            for sgid, sg in enumerate(self.subgoalsSet[:self.nbSubgoalsSetInitially]):
                if title:
                    row.append("AVGNumSRLpePagetoSG" + str(sgid) + "AnyTime")
                else:
                    cptSrl = 0
                    cptPage = 0
                    for page in self.SRLPagesRelevantSubgoalAnytime[sg]:
                        cptPage += 1
                        cptSrl += self.SRLPagesRelevantSubgoalAnytime[sg][page]
                    try:
                        row.append(cptSrl/float(cptPage))
                    except ZeroDivisionError:
                        row.append("N/A")

        elif dataType == "ActionsFeaturesNoCorrel":
            #convert timedelts to miliseconds

            if title:
                row.extend(["DurationDay2", "TimeSpentWithContentOverall",
                            "TimePageRelSG", "TimePageIrrelSG",
                            "TotalTimeWithRelTextContent", "TotalTimeWithRelFullContent", "TotalTimeWithIrrelTextContent", "TotalTimeWithIrrelFullContent",
                            "NumberSG", "TotalTimeSettingSG",
                            "NoteTakingDuration", "NoteCheckingDuration", "NoteCheckingNum",
                            "TimePaperNotes", "TimeINF","FlagWorkedWithoutSubgoal"
                            ])
                    #row.extend(["RatioRelevantPagesToInitialSubgoalsVisitedMoreThan15sWhileWorkingOnThem", "RatioIrrelevantPagesToInitialSubgoalsVisitedMoreThan15sWhileWorkingOnThem"])
                for sgid, _ in enumerate(self.ratioPagesRelevantToInitialSubgoalsReadActive):
                    row.append("RatioPagesRelevantToInitialSubgoal" + str(sgid+1) + "ReadWhenSubgoal" + str(sgid+1) + "Active")
                for sgid, _ in enumerate(self.ratioPagesRelevantToInitialSubgoalsReadAnytime):
                    row.append("RatioPagesRelevantToInitialSubgoal" + str(sgid+1) + "ReadAtAnytime")
            else:
                def TimeDelta2Miliseconds(td):
                    return td.seconds * 1000 + td.microseconds/1000
#                 row.extend([TimeDelta2Miliseconds(self.DurationDay2), TimeDelta2Miliseconds(self.pageTotalTimeOverall),
#                             TimeDelta2Miliseconds(self.pagesTotalTimeSpentRelevantSG), TimeDelta2Miliseconds(self.pagesTotalTimeSpentIrrelSG),
#                             TimeDelta2Miliseconds(self.timeSpentWithContentNoImageRel), TimeDelta2Miliseconds(self.timeSpentWithContentImageRel), TimeDelta2Miliseconds(self.timeSpentWithContentNoImageIrrel), TimeDelta2Miliseconds(self.timeSpentWithContentImageIrrel),
#                             self.NbSGTotal, self.SGTimeTotal.seconds,
#                             Utils.getMilliSecondsFromDatetime(self.noteTakingDuration), Utils.getMilliSecondsFromDatetime(self.noteCheckingDuration), self.nbNoteChecking,
#                             TimeDelta2Miliseconds(self.DurationNoteTakenOnPaper),TimeDelta2Miliseconds(self.DurationUserTypingINF)
#                             ])
                row.extend([TimeDelta2Miliseconds(self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.pageTotalTimeOverall, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.pagesTotalTimeSpentRelevantSG, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.pagesTotalTimeSpentIrrelSG, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.timeSpentWithContentNoImageRel, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.timeSpentWithContentImageRel, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.timeSpentWithContentNoImageIrrel, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.timeSpentWithContentImageIrrel, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.NbSGTotal, self.DurationMTInteractionDay2, False),
                            self.AveragedOverX(self.SGTimeTotal.seconds, self.DurationMTInteractionDay2, False),
                            self.AveragedOverX(Utils.getMilliSecondsFromDatetime(self.noteTakingDuration), self.DurationMTInteractionDay2, False),
                            self.AveragedOverX(Utils.getMilliSecondsFromDatetime(self.noteCheckingDuration), self.DurationMTInteractionDay2, False),
                            self.AveragedOverX(self.nbNoteChecking, self.DurationMTInteractionDay2, False),
                            self.AveragedOverX(self.DurationNoteTakenOnPaper, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.DurationUserTypingINF, self.DurationMTInteractionDay2)
                            ])

                if self.workedWithoutSubgoals == True:
                    row.append(1)
                else:
                    row.append(0)
                #print self.ID," Note Taking", self.noteTakingDuration
                #print self.ID," Note Checking", self.noteCheckingDuration
                #add number of pages relevant to sg
                row.extend(self.ratioPagesRelevantToInitialSubgoalsReadActive)
                row.extend(self.ratioPagesRelevantToInitialSubgoalsReadAnytime)
            #add features relevant to SRL
            for srl in ["PLAN", "MPTG", "JOL", "FOK", "CE", "INF"]:
                if title:
                    row.append("num"+srl)
                else:
                    row.append(self.AveragedOverX(self.SRL[srl], self.DurationMTInteractionDay2, False))
#             for sgid, sg in enumerate(self.subgoalsSet[:self.nbSubgoalsSetInitially]):
#                 if title:
#                     row.append("AVGNumSRLperPagetoSG" + str(sgid)+"Active")
#                 else:
#                     cptSrl = 0
#                     cptPage = 0
#                     for page in self.SRLPagesRelevantSubgoalWhenActive[sg]:
#                         cptPage += 1
#                         cptSrl += self.SRLPagesRelevantSubgoalWhenActive[sg][page]
#                     try:
#                         row.append(cptSrl/float(cptPage))
#                     except ZeroDivisionError:
#                         row.append("N/A")
            for sgid, sg in enumerate(self.subgoalsSet[:self.nbSubgoalsSetInitially]):
                if title:
                    row.append("AVGNumSRLpePagetoSG" + str(sgid) + "AnyTime")
                else:
                    cptSrl = 0
                    cptPage = 0
                    for page in self.SRLPagesRelevantSubgoalAnytime[sg]:
                        cptPage += 1
                        cptSrl += self.SRLPagesRelevantSubgoalAnytime[sg][page]
                    try:
                        row.append(cptSrl/float(cptPage))
                    except ZeroDivisionError:
                        row.append("N/A")
            #add number of images opened
            if title:
                row.extend(["ImagesOpened_num", "TimeFullView_total"])
            else:
                row.extend([self.AveragedOverX(self.numImagesOpen,self.DurationDay2, False), self.AveragedOverX(self.TimeFullView_total, self.DurationDay2)])


        elif dataType == "NatashaDariaFeatures":
            #convert timedelts to miliseconds

            if title:
                row.extend(["DurationDay2InSecs", "TimeSpentWithContentOverall",
                            "TimePageRelSG", "TimePageIrrelSG",
                            "TotalTimeWithRelTextContent", "TotalTimeWithRelFullContent", "TotalTimeWithIrrelTextContent", "TotalTimeWithIrrelFullContent",
                            "NumberSG", "TotalTimeSettingSG",
                            "TimePaperNotes", "TimeINF"
                            ])
                    #row.extend(["RatioRelevantPagesToInitialSubgoalsVisitedMoreThan15sWhileWorkingOnThem", "RatioIrrelevantPagesToInitialSubgoalsVisitedMoreThan15sWhileWorkingOnThem"])
                for sgid, _ in enumerate(self.ratioPagesRelevantToInitialSubgoalsReadActive):
                    row.append("RatioPagesRelevantToInitialSubgoal" + str(sgid+1) + "ReadWhenSubgoal" + str(sgid+1) + "Active")
                for sgid, _ in enumerate(self.ratioPagesRelevantToInitialSubgoalsReadAnytime):
                    row.append("RatioPagesRelevantToInitialSubgoal" + str(sgid+1) + "ReadAtAnytime")
            else:
                def TimeDelta2Miliseconds(td):
                    return td.seconds * 1000 + td.microseconds/1000
#                 row.extend([TimeDelta2Miliseconds(self.DurationDay2), TimeDelta2Miliseconds(self.pageTotalTimeOverall),
#                             TimeDelta2Miliseconds(self.pagesTotalTimeSpentRelevantSG), TimeDelta2Miliseconds(self.pagesTotalTimeSpentIrrelSG),
#                             TimeDelta2Miliseconds(self.timeSpentWithContentNoImageRel), TimeDelta2Miliseconds(self.timeSpentWithContentImageRel), TimeDelta2Miliseconds(self.timeSpentWithContentNoImageIrrel), TimeDelta2Miliseconds(self.timeSpentWithContentImageIrrel),
#                             self.NbSGTotal, self.SGTimeTotal.seconds,
#                             Utils.getMilliSecondsFromDatetime(self.noteTakingDuration), Utils.getMilliSecondsFromDatetime(self.noteCheckingDuration), self.nbNoteChecking,
#                             TimeDelta2Miliseconds(self.DurationNoteTakenOnPaper),TimeDelta2Miliseconds(self.DurationUserTypingINF)
#                             ])
                row.extend([TimeDelta2Miliseconds(self.DurationMTInteractionDay2/1000),
                            self.AveragedOverX(self.pageTotalTimeOverall, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.pagesTotalTimeSpentRelevantSG, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.pagesTotalTimeSpentIrrelSG, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.timeSpentWithContentNoImageRel, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.timeSpentWithContentImageRel, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.timeSpentWithContentNoImageIrrel, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.timeSpentWithContentImageIrrel, self.DurationMTInteractionDay2),
                            self.NbSGTotal,
                            self.AveragedOverX(self.SGTimeTotal.seconds, self.DurationMTInteractionDay2, False),
                            self.AveragedOverX(self.DurationNoteTakenOnPaper, self.DurationMTInteractionDay2),
                            self.AveragedOverX(self.DurationUserTypingINF, self.DurationMTInteractionDay2)
                            ])
                #print self.ID," Note Taking", self.noteTakingDuration
                #print self.ID," Note Checking", self.noteCheckingDuration
                #add number of pages relevant to sg
                row.extend(self.ratioPagesRelevantToInitialSubgoalsReadActive)
                row.extend(self.ratioPagesRelevantToInitialSubgoalsReadAnytime)

            #add number of images opened
            if title:
                row.extend(["ImagesOpened_num", "TimeFullView_total"])
            else:
                row.extend([self.numImagesOpen, self.AveragedOverX(self.TimeFullView_total, self.DurationDay2)])


        #--------
        else:
            logger.warning("Unknown type of information to display:" + dataType)
        return self.getSummaryRowList(logger, dataTypes[1:], row, title)      # recursion with the rest of the dataTypes and the updated row


    def getSummaryRowString(self, logger, subjectData=False, experimentData=False, pageData=False, eventsData=False, SRLData=False):
        """Return a chosen set of information about the subject as a string where data elements are separated by \t"""
        data = []
        if subjectData:
            data.extend(self.getSummaryRowList(logger, ["subject"], []))
        if experimentData:
            data.extend(self.getSummaryRowList(logger, ["experiment"], []))
        if pageData:
            data.extend(self.getSummaryRowList(logger, ["pagesViewEvents"], []))
        if eventsData:
            data.extend(self.getSummaryRowList(logger, ["allEvents"], []))
        if SRLData:
            data.extend(self.getSummaryRowList(logger, ["SRLEvents"], []))
        toprint = ""
        for elt in data:
            toprint += str(elt) + "\t"
        return toprint[:-1] + "\n"


#    def getInfoString(self):
#        """Return a predefined set of information about the subject as a string"""
#        return self.ID + ":" + str(self.experimenters) + " " + self.group + " " + self.name + " " + self.gender + " " + self.age + " " + self.ethnicity + " " + self.education + " " + self.GPA + " " + self.major + " " + self.school + " " + str(self.nbCourses) + "\n"


#    def getSRLString(self, SRLEvent):
#        """Return a string containing all the events of day 2"""
#        s = ""
#        for event in self.day2Events:
#            if isinstance(event, SRLEvent):
#                s+= event + "\


    def getEvents(self, types, day=0, around=False, typesAround=[], timeBefore=datetime.timedelta(microseconds=0), timeAfter=datetime.timedelta(microseconds=0)):
        """Retrieve all the events from a given list of types for this subject, during his day 1 (1), 2 (2) or both (0).
        It can also include events taking place around the events from the previous list if around=True,
        in which case it will consider events that were taking place a certain time before/after depending on timeBefore/timeAfter values"""
        retrievedEvtList = []
        allEvtList = []

        if day == 1 or day == 0:
            allEvtList.extend(self.day1AllEvents)
        if day == 2 or day == 0:
            allEvtList.extend(self.day2AllEvents)

        # if the event is of one of the types to be retrieved, add it to a list
        for event in allEvtList:
            for typei in types:
                if isinstance(event, typei):
                    retrievedEvtList.append(event)
                    #print event.getTimeStart()

        # get events around the previously retrieved ones, if requested
        if around:
            timesAround = []
            extraRetrievedEvtList = []
            # build a list of time ranges ([start, end]) to consider
            for event in retrievedEvtList:
                timesAround.append([event.getTimeStart() - timeBefore, event.getTimeEnd() + timeAfter])
            # check for each event if it's in one of the time ranges from the list
            for event in allEvtList:
                if event not in retrievedEvtList:   # no need to consider events already retrieved
                    for typei in typesAround:        # if the type of the event is to be considered
                        if isinstance(event, typei):
                            for time in timesAround:
                                if event.getTimeStart() > time[0] and event.getTimeEnd() < time[1]:
                                    extraRetrievedEvtList.append(event)
            # add those extra elements to the original list and sort it to have events in chronological order
            retrievedEvtList.extend(extraRetrievedEvtList)
            retrievedEvtList.sort(key=lambda t: (t.getTimeStart().hour, t.getTimeStart().minute, t.getTimeStart().second, t.getTimeStart().microsecond))

        return retrievedEvtList

    def getAllEvents(self, day=0):
        allEvtList = []

        if day == 1 or day == 0:
            allEvtList.extend(self.day1AllEvents)
        if day == 2 or day == 0:
            allEvtList.extend(self.day2AllEvents)

        return allEvtList

    def getEventListAsList(self, typesNFields, day=0):
        """Return a list containing information about events from a given list of types"""
        types = map(lambda x: x[0], typesNFields)
        fields = map(lambda x: x[1], typesNFields)
        evtList = self.getEvents(types, day)

        allEvtList= []
        for event in evtList:
#            print "xxxx " + str(event)
#            print types
#            print type(event)
#            print type(event).__bases__
            ls = [self.ID]
            try:    # get the index of this event according to its class
                idx = types.index(type(event))
            except ValueError:  # if the parameter was the parent class, look for it
                idx = types.index(type(event).__bases__[0])
            if fields[idx] == {}:
                l = map(lambda x: str(x), event.getInfo(showAll=True))
            else:
                l = map(lambda x: str(x), event.getInfo(**fields[idx]))
            for i in l:
                ls.append(i)
            allEvtList.append(ls)

        return allEvtList


    def getEventListAsString(self, typesNFields, day=0):
        """Return a tab separated list of strings containing information about events from a given list of types"""
        allEvtText = ""
        l = self.getEventListAsList(typesNFields, day)
        for evt in l:
            for field in evt:
                allEvtText += field + "\t"
            allEvtText = allEvtText[:-1] + "\n"
        return allEvtText


    def getPageInViewWhenEvent(self, logger, event):
        """Check in the log of events which page the participant was viewing when one of the events from this log took place"""
        if event in self.day2AllEvents:
            idxEvt = self.day2AllEvents.index(event)    # retrieve all the elements that could be relevant
            li = reversed(self.day2AllEvents[:idxEvt])  # get a reverse list iterator of events before
            for i in li:                                # check for the first page event and get the ID to return it
                if isinstance(i, Browsing.MTBrowsingPageEvent):
                    return i.pageIdx
        else:
            logger.error("Event " + event.getInfo(showAll=True) + " wasn't found in the list of events of participant " + self.ID)
            return - 1


    def getSubgoalWhenEvent(self, logger, event):
        """Check in the log of events which subgoal the participant was trying to achieve when one of the events from this log took place"""
        if event in self.day2AllEvents:
            idxEvt = self.day2AllEvents.index(event)    # retrieve all the elements that could be relevant
            li = reversed(self.day2AllEvents[:idxEvt])  # get a reverse list iterator of events before
            for i in li:
                if isinstance(i, Custom.CEvtPursuingNewSubgoal):
                    return i.currentSubgoalID
            logger.error("No subgoal found before event " + str(event.getInfo(showAll=True)) + " for participant " + self.ID)
            return -2
        else:
            logger.error("Event " + str(event.getInfo(showAll=True)) + " wasn't found in the list of events of participant " + self.ID)
            return - 1

    def calculateLearningGain(self, preScore, postScore):
        """Calculate learning gain based on the two given scores (from 0 to 1)"""
        if (preScore != 1):
            return 100*(postScore - preScore)/(1 - preScore)
        else:
            return 0    # no possible learning gain when maximum score was already obtained in the pretest

    def calculateLearningGainWithoutLosses(self, preScore, postScore):
        """Calculate the leaning gain based on the two given scores (from 0 to 1) but consider that one can't unlearn, and therefore that a negative learning gain should be counted as 0"""
        res = self.calculateLearningGain(preScore, postScore)
        if res < 0:
            return 0
        else:
            return res
