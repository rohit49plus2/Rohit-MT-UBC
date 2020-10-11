'''
Created on 2012-10-12

@author: Francois
'''

import datetime
import time
from Events import *
#from MetaTutor.loganalyzer import MTLogAnalyzer
#from MetaTutor.MTSubject import MTSubject

class MTLogParser(object):
    '''
    classdocs
    '''

    def getIdxOfLastListEltWithPattInPos(self, logger, l, patt, pos=0, reportError=True):
        """Get the index of the last element in a list of lists, such as that inner list has a given pattern in the position given as parameter.

        @type logger:Logger
        @param logger: the logging element used to display message in the console
        @type    l: list
        @param   l: the list considered for the search
        @type    patt: string
        @param   patt: the pattern looked for in every inner list of l
        @type    pos: number
        @param   pos: the position where the pattern should be in an inner list. Is worth 0 by default.
        @type    reportError: boolean
        @param    reportError: whether or not an error message should be displayed if the element isn't found. Set it to False if it can be normal not to find a pattern in the list (e.g., "MTRuleTNEvent" and "RulePKAorINForSUMM")
        """
        l.reverse()
        try:
            idx = list(map((lambda x: x[pos]), l)).index(patt)
        except IndexError:
            if reportError:
                logger.error("At least some elements of the list given in parameter have a length inferior to " + str(pos))
            raise
        except ValueError:
            if reportError:
                logger.error("The pattern " + patt + " couldn't be found in position " + str(pos) + " of any inner list")
            raise
        except:
            if reportError:
                logger.error("Unknown error")
            raise
        l.reverse()
        # Convert the index in the referential of the non-reversed list
        return ((len(l) - 1) - idx)


    def isInListEltWithPattInPos(self, l, patt, pos=0):
        """Test if in a list of lists, one of the inner list has a given pattern in the position given as parameter.

        @type    l: list
        @param   l: the list considered for the search
        @type    patt: string
        @param   patt: the pattern looked for in every inner list of l
        @type    pos: number
        @param   pos: the position where the pattern should be in an inner list. Is worth 0 by default."""

        try:
            list(map((lambda x: x[pos]), l)).index(patt)
        except ValueError:
            return False
        else:
            return True


    def parseDay1LogEvents(self, logger, mtsubject, matTestCorrectAnswers):
        ongoingSRLTest = False
        pretestCanBeA = True
        pretestCanBeB = True
        doneWithSRLTest = False
        if mtsubject.logLOD == 2:
            doneWithSRLTest = True
        elif (mtsubject.logLOD != 0 and mtsubject.logLOD !=1):
            logger.warning("Check if SRL test was performed with this version of MetaTutor")
        ongoingPreTest = False
        queuedEvts = []

        for event in mtsubject.day1Events:
            if isinstance(event, Layout.MTLayoutEvent):
                if event.layout == "InputEnlarged": # the input area is enlarged when the user is taking one of the 2 quizzes
                    if not doneWithSRLTest:
                        queuedEvts.append(["CEvtUserTakingSRLTest", event.timestamp, event])
                        ongoingSRLTest = True
                    elif ongoingPreTest:
                        logger.warning("The layout changed while the user had already taken both the SRL and the Pre Tests")
                    else:
                        queuedEvts.append(["CEvtUserTakingPreTest", event.timestamp, event])
                        ongoingPreTest = True

            elif isinstance(event, Dialog.MTDialogAgentEvent):
                if event.scriptID == "Quiz finished":       # when the SRL test is over, create a corresponding quiz event with the score
                    if not ongoingSRLTest:
                        logger.warning("The SRL quiz is said to have ended but was supposed to be over already")
                    ongoingSRLTest = False
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTakingSRLTest"))
                    try:
                        eventQuizElements = evtInfos[3]
                    except IndexError:
                        eventQuizElements = []
                        logger.warning("A queued CEvtUserTakingSRLTest event doesn't have any quiz element associated to it")
                    mtsubject.day1ExtEvents.append(Custom.CEvtUserTakingSRLTest(logger, evtInfos[1], event.timestamp, evtInfos[2], eventQuizElements))
                    doneWithSRLTest = True
                elif event.scriptID == "Pretest finished":  # when the PreTest is over, create a corresponding quiz event with the score
                    if not ongoingPreTest:
                        logger.warning("The pretest quiz is said to have ended but was supposed to be over already")
                    ongoingPreTest = False
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTakingPreTest"))

                    # save the category of the pretest in the subject infos
                    if (pretestCanBeA and not(pretestCanBeB)):
                        mtsubject.testsVersion = ["A", "B"]
                        #print "Pretest A"
                    elif (pretestCanBeB and not(pretestCanBeA)):
                        mtsubject.testsVersion = ["B", "A"]
                        #print "Pretest B"
                    elif (not(pretestCanBeA) and not(pretestCanBeB)):
                        logger.error("The pretest doesn't seem to match either known test version (A or B) - the matrix is wrong or the questionnaire must have changed")
                    else:   # can be both
                        logger.warning("Couldn't determine the version of the pretest based on participant's replies to it")

                    try:
                        eventQuizElements = evtInfos[3]
                    except IndexError:
                        eventQuizElements = []
                        logger.warning("A queued CEvtUserTakingPreTest event doesn't have any quiz element associated to it")
                    mtsubject.day1ExtEvents.append(Custom.CEvtUserTakingPreTest(logger, evtInfos[1], event.timestamp, evtInfos[2], eventQuizElements))

            elif isinstance(event, Quiz.MTQuizEvent):
                if not (ongoingSRLTest or ongoingPreTest):
                    logger.warning("A quiz question is happening out of the context of any quiz: " + str(event.getInfo(showAll=True)))       # it shouldn't happen
                else:
                    # if this the pretest, try to determine if it's version A or B by checking if the answer (A, B, C or D) and its validity are compatible with each version
                    if (event.category == "Circulatory test"):
                        if not((event.answerCorrect and matTestCorrectAnswers[0][int(event.questionID[1:])-1] == event.answerType) or (not(event.answerCorrect) and matTestCorrectAnswers[0][int(event.questionID[1:])-1] != event.answerType)):
                            pretestCanBeA = False
                        if not((event.answerCorrect and matTestCorrectAnswers[1][int(event.questionID[1:])-1] == event.answerType) or (not(event.answerCorrect) and matTestCorrectAnswers[1][int(event.questionID[1:])-1] != event.answerType)):
                            pretestCanBeB = False
                    # add the quiz event to the event under construction
                    idxQuiz = (self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTakingSRLTest") if ongoingSRLTest else self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTakingPreTest"))
                    if len(queuedEvts[idxQuiz]) == 3:        # if it's the first one
                        queuedEvts[idxQuiz].append([event])
                    elif len(queuedEvts[idxQuiz]) == 4:     # if some have already been added
                        queuedEvts[idxQuiz][3].append(event)
                    else:
                        logger.warning("A queued CEvtUserTakingSRLTest or CEvtUserTakingPreTest had a length of " + str(len(queuedEvts[idxQuiz])) + "instead of 3 or 4: " + str(queuedEvts[idxQuiz]))

        if (queuedEvts != []):
            logger.warning("List of remaining queued events for day 1 (should be empty): " + str(queuedEvts))
        # Make a chronological list of ALL events for day 1, not to have to fusionate them all the time for that
        mtsubject.day1AllEvents = list(mtsubject.day1Events)              # make a copy of the original events list
        mtsubject.day1AllEvents.extend(mtsubject.day1ExtEvents)       # add the extended events to the copy
        mtsubject.day1AllEvents.sort(key=lambda t: (t.getTimeStart().hour, t.getTimeStart().minute, t.getTimeStart().second, t.getTimeStart().microsecond))


    def parseDay2LogEvents(self, logger, mtsubject, matPageSubgoalDict, possibleSubgoalsNamesID, stopTimeStamp=None, startTimeStamp=None):
        """Analyze the log events in order to generate extra higher order events based on particular patterns and cooccurrences of events"""

        debug = False
        if debug:
            print("stop time stamp", stopTimeStamp)
            print("start time stamp", startTimeStamp)
            time.sleep(3)

        # Booleans to track if a particular event has started and one is waiting for it to end
        agentSpeaking = False
        agentRemindingTimeLeft = False
        waitingForStudentInput = False
        waitingForEndQuiz = False
        waitingForEndNotes = False
        waitingForDependsValue = False
        waitingForEndFirstGoals = False
        waitingForEndNewGoal = False
        waitingForPostTestReady = False
        waitingForPostTestStart = False
        waitingForPostTestEnd = False
        waitingForPostpone = False
        waitingForSGStay = False
        waitingForSummaryAdditionToNotes = False
        waitingForCE = False
        waitingForMPTG = False
        waitingForJOL = False
        waitingForFOK = False
        waitingForEndTypingPKA = False
        waitingForEndTypingINF = False
        waitingForEndTypingSUMM = False
        waitingForVideoEnd = False
        waitingForQuestionnaireEnd = False
        waitingForPenEnd = False
        waitingForGoalPick = False
        waitingToConfirmTwoSG = False
        inGoalSettingPhase = False
        prevPageInView = ""
        goalCounter = 1
        timeQuestionnairePaused = datetime.timedelta(0, 0, 0)
        timePreviousQuestionnairePaused = datetime.timedelta(0, 0, 0)
        timeSystemPaused = datetime.timedelta(0, 0, 0)
        timeVideoPaused = datetime.timedelta(0, 0, 0)
        systemPaused = False
        videoPaused = False
        goalQueue = []      # the current goal is therefore goalQueue[0] if it exists
        goalsToRemove = []  # list of the lastly added goals, for the case when 2 goals are set at once, while 2 had already been set before, triggering a PamSubgoalTooMany that should cancel the last 2 goals to make the user pick one only

        #: Queue of events that have been started and not yet used to actually generate an event
        queuedEvts = []
        #: Special separated queue for the Depends kind of events
        queuedDepends = []

        #bondaria----------------

        startedBrowsing = False #flag that indicates that reading session started
        #required to find if user is reading
        #durationPKA = datetime.timedelta(0, 0, 0)
        durationSRL = datetime.timedelta(0, 0, 0)
        durationQuiz = datetime.timedelta(0, 0, 0)
        beforeImagetimeQuestionnairePaused = datetime.timedelta(0, 0, 0)
        beforeImagetimeSystemPaused = datetime.timedelta(0, 0, 0)
        beforeImagetimeVideoPaused = datetime.timedelta(0, 0, 0)
        beforeImagedurationSRL = datetime.timedelta(0,0,0)
        beforeImagedurationQuiz = datetime.timedelta(0,0,0)
        timeImageInView = datetime.timedelta(0, 0, 0)
        flagImageOpen = False
        #numImagesOpen = 0 #number of Images opened
        #------------------------

        initialSubgoalsSet = False # NJ Added
        firstCEvtPursuingNewSubgoalAppended = False

        for iEv, event in enumerate(mtsubject.day2Events):
            #print iEv
            if debug:
                print (event.getInfo()[0], event.timestamp)

            """if event.timestamp >= stopTimeStamp:
                print "EVENT TIME STAMP >= STOP TIME STAMP"
            if initialSubgoalsSet:
                print "INITIAL SUBGOALS SET"
            if firstCEvtPursuingNewSubgoalAppended:
                print "FIRST SUBGOAL APPENDED"""

            if stopTimeStamp != None and event.timestamp >= stopTimeStamp and initialSubgoalsSet: # firstCEvtPursuingNewSubgoalAppended: doesn't always happen
                print( "Stopping parseDay2Loop at", event.timestamp)
                time.sleep(0.1)
                break

            if isinstance(event, Browsing.MTBrowsingEvent):                        ### TYPE 1
                if isinstance(event, Browsing.MTBrowsingVideoEvent):
                    if event.play == "Start":
                        if self.isInListEltWithPattInPos(queuedEvts, "CEvtVideoIsPlaying"):
                            logger.warning("A new video is starting while the previous one hasn't ended properly")
                        queuedEvts.append(["CEvtVideoIsPlaying", event.timestamp, event.videoName])
                        waitingForVideoEnd = True
                    elif event.play == "End" and waitingForVideoEnd:
                        # retrieve information about this element from the list of queued events to be treated
                        # it is found according to its first field and taken out of the queue at the same time
                        evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtVideoIsPlaying"))
                        # create a relevant event and append it to the list of custom events
                        mtsubject.day2ExtEvents.append(Custom.CEvtVideoIsPlaying(logger, evtInfos[1], event.timestamp, evtInfos[2]))
                        waitingForVideoEnd = False
                    else:
                        logger.warning("Unknown kind of MTBrowsingVideoEvent: " + event.play)

                elif isinstance(event, Browsing.MTBrowsingQuestionnaire):
                    # same model as video playing above
                    if event.status == "Start":
                        if self.isInListEltWithPattInPos(queuedEvts, "CEvtQuestionnaireOngoing"):
                            logger.warning("A new questionnaire is starting while the previous one hasn't ended properly")
                        queuedEvts.append(["CEvtQuestionnaireOngoing", event.timestamp, event.questionnaireName])
                        waitingForQuestionnaireEnd = True
                        timePreviousQuestionnairePaused = timeQuestionnairePaused   # save time from a potential previous questionnaire while being on the same page
                        timeQuestionnairePaused = event.timestamp    # the timer starts being paused
                    elif event.status == "End" and waitingForQuestionnaireEnd:
                        evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtQuestionnaireOngoing"))
                        mtsubject.day2ExtEvents.append(Custom.CEvtQuestionnaireOngoing(logger, evtInfos[1], event.timestamp, evtInfos[2]))
                        if event.questionnaireName == "EIV":
                            #print evtInfos
                            #print event.absoluteTime
                            #print event.timestamp
                            mtsubject.day2ExtEvents.append(Questionnaire.MTQuestionnaireEIV(logger, evtInfos[1], event.absoluteTime, event.timestamp))
                        waitingForQuestionnaireEnd = False
                        timeQuestionnairePaused = event.timestamp - timeQuestionnairePaused   # the timer ends being paused
                        timeQuestionnairePaused += timePreviousQuestionnairePaused      # add time from a previous questionnaire while being on the same page, if any
                        timePreviousQuestionnairePaused = datetime.timedelta(0, 0, 0)
                    else:
                        logger.warning("Unknown kind of MTBrowsingVideoEvent: " + event.status)

                elif isinstance(event, Browsing.MTBrowsingPageEvent):   # calculate the time spent on the previous page, now that it is changing
                    #bondaria
                    startedBrowsing = True #browsing session started. Needed to track SRL processes when during reading session
                    #------------------
                    if prevPageInView != "":
                        prevPageInView.timeSpentOverall = event.timestamp - prevPageInView.timestamp
                        #prevPageInView.timeSpentWithContent = prevPageInView.timeSpentOverall - (timeQuestionnairePaused + timeSystemPaused + timeVideoPaused)      # also substract time spent on questionnaires, watching videos and system pauses, as it's not time spent reading
                        prevPageInView.timeSpentWithContent = prevPageInView.timeSpentOverall - (timeQuestionnairePaused + timeSystemPaused + timeVideoPaused + durationSRL + durationQuiz)      # also substract time spent on questionnaires, watching videos and system pauses, as it's not time spent reading
                        #bonadria-----------
                        #calculate time in respect to image enlarged or not
                        if flagImageOpen == False: #there was no image open
                            prevPageInView.timeSpentWithContentImage = datetime.timedelta(0, 0, 0)
                            prevPageInView.timeSpentWithContentNoImage = prevPageInView.timeSpentWithContent
                            if prevPageInView.relevantToSubgoal > 0: #if page is relevant to subgoal
                                prevPageInView.timeSpentWithContentNoImageRel = prevPageInView.timeSpentWithContent
                            else: #if the page is not relevant
                                prevPageInView.timeSpentWithContentNoImageIrrel = prevPageInView.timeSpentWithContent

                        else: #image was open
                            #deltaImage = (timeQuestionnairePaused + timeSystemPaused + timeVideoPaused) - (beforeImagetimeQuestionnairePaused + beforeImagetimeSystemPaused + beforeImagetimeVideoPaused)
                            deltaImage = (timeQuestionnairePaused + timeSystemPaused + timeVideoPaused + durationSRL + durationQuiz) - (beforeImagetimeQuestionnairePaused + beforeImagetimeSystemPaused + beforeImagetimeVideoPaused + beforeImagedurationSRL + beforeImagedurationQuiz)
                            prevPageInView.timeSpentWithContentImage = event.timestamp - timeImageInView - deltaImage
                            prevPageInView.timeSpentWithContentNoImage = prevPageInView.timeSpentWithContent - prevPageInView.timeSpentWithContentImage
                            # the following FOUR features correspond to Full Content vs. Text-Only Content available on screen + Relevant to SG or Not Relevant to SG
                            if prevPageInView.relevantToSubgoal > 0: #if page is relevant to subgoal
                                prevPageInView.timeSpentWithContentImageRel = event.timestamp - timeImageInView - deltaImage
                                prevPageInView.timeSpentWithContentNoImageRel = prevPageInView.timeSpentWithContent - prevPageInView.timeSpentWithContentImage
                            else: #if the page is not relevant
                                prevPageInView.timeSpentWithContentImageIrrel = event.timestamp - timeImageInView - deltaImage
                                prevPageInView.timeSpentWithContentNoImageIrrel = prevPageInView.timeSpentWithContent - prevPageInView.timeSpentWithContentImage

                            if prevPageInView.timeSpentWithContentImage<datetime.timedelta(0, 0, 0) :
                                #check needed if Time spent on Page with Image Content is larger than
                                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                print(event.pageIdx)
                                print("deltaPage: ", (timeQuestionnairePaused + timeSystemPaused + timeVideoPaused + durationSRL + durationQuiz))
                                print( "deltabeforeImage: ", (beforeImagetimeQuestionnairePaused + beforeImagetimeSystemPaused + beforeImagetimeVideoPaused + beforeImagedurationSRL + beforeImagedurationQuiz))
                                print( "Questionnaire: ", timeQuestionnairePaused)
                                print( "System pause: ", timeSystemPaused)
                                print( "Video: ", timeVideoPaused )
                                print( "SRL: ", durationSRL )
                                print( "Quiz: ", durationQuiz)
                                print( "Page finished: ", event.timestamp)
                                print( "Time user spent with content: ", prevPageInView.timeSpentWithContentImage)
                                print( "Timestamp of Image appearing on screen: ", timeImageInView)
                                print( "DeltaImage: ", deltaImage)
                                print( "!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        beforeImagetimeQuestionnairePaused = datetime.timedelta(0, 0, 0)
                        beforeImagetimeSystemPaused = datetime.timedelta(0, 0, 0)
                        beforeImagetimeVideoPaused = datetime.timedelta(0, 0, 0)
                        beforeImagedurationSRL = datetime.timedelta(0, 0, 0)
                        beforeImagedurationQuiz = datetime.timedelta(0, 0, 0)
                        flagImageOpen = False
                        deltaImage = datetime.timedelta(0, 0, 0)
                        #-------------------
                        durationSRL = datetime.timedelta(0,0,0)
                        durationQuiz = datetime.timedelta(0,0,0)
                        # reinitialize timers for the next page
                        timeQuestionnairePaused = datetime.timedelta(0, 0, 0)
                        timeSystemPaused = datetime.timedelta(0, 0, 0)
                        timeVideoPaused = datetime.timedelta(0, 0, 0)
                    prevPageInView = event
                    # Also, memorize if the page view is relevant or not to the current subgoal
                    if len(goalQueue) > 0:
                        event.relevantToSubgoal = matPageSubgoalDict[mtsubject.study][goalQueue[0] - 1][int(event.pageIdx)]
                        #event.relevantToSubgoal = matPageSubgoal[goalQueue[0] - 1][int(event.pageIdx)]
                    else:
                        event.relevantToSubgoal = -1
                #bondaria---------------------
                elif isinstance(event, Browsing.MTBrowsingImageEvent):
                    #print "Browsing Image Event"
                    #beforeImagetimeQuestionnairePaused = datetime.timedelta(0, 0, 0)
                    #beforeImagetimeSystemPaused = datetime.timedelta(0, 0, 0)
                    #beforeImagetimeVideoPaused = datetime.timedelta(0, 0, 0)
                    beforeImagetimeQuestionnairePaused = timeQuestionnairePaused
                    beforeImagetimeSystemPaused = timeSystemPaused
                    beforeImagetimeVideoPaused = timeVideoPaused
                    beforeImagedurationSRL = durationSRL
                    beforeImagedurationQuiz = durationQuiz
                    timeImageInView = event.timestamp
                    flagImageOpen = True
                    #numImagesOpen += 1
                #--------------------------------
                elif isinstance(event, Browsing.MTBrowsingRestoreAfterCrash):
                    # when the system crashes, it doesn't record if it was waiting for a Student Input
                    (agentSpeaking, agentRemindingTimeLeft, waitingForStudentInput,
                    waitingForEndQuiz, waitingForEndNotes, waitingForDependsValue,
                    waitingForEndFirstGoals, waitingForEndNewGoal, waitingForPostTestReady,
                    waitingForPostTestStart, waitingForPostTestEnd, waitingForPostpone,
                    waitingForSummaryAdditionToNotes, waitingForCE, waitingForMPTG,
                    waitingForJOL, waitingForFOK, waitingForEndTypingPKA,
                    waitingForEndTypingINF, waitingForEndTypingSUMM, waitingForVideoEnd,
                    waitingForPenEnd) = (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
                    queuedEvts = []
                    queuedDepends = []

            elif isinstance(event, Digimemo.MTDigimemoEvent):                      ### TYPE 6
                if event.type == "On":
                    if self.isInListEltWithPattInPos(queuedEvts, "CEvtNoteTakenOnPaper"):
                        logger.warning("New note is being taken with the pen while previous one hasn't ended properly")
                    queuedEvts.append(["CEvtNoteTakenOnPaper", event.timestamp])
                    waitingForPenEnd = True
                elif event.type == "Off" and waitingForPenEnd:
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtNoteTakenOnPaper"))
                    mtsubject.day2ExtEvents.append(Custom.CEvtNoteTakenOnPaper(logger, evtInfos[1], event.timestamp))
                    waitingForPenEnd = False
                else:
                    logger.warning("Unknown type for MTDigimemoEvent: " + event.type)

            elif isinstance(event, Agent.MTAgentTalkEvent):                        ### TYPE 8
                # To prevent a bug with the time reminder event being labeled with the latest previous event ID
                # one needs to deal with them based on the text and BEFORE any other type 8 event
                if event.text in ["You have 10 minutes left.", "You have 5 minutes left."]:
                    queuedEvts.append(["CEvtAgentRemindsTimeLeft", event.timestamp, event.absoluteTime, event.agentName, (5 if "5" in event.text else 10)])
                    agentSpeaking = True
                    agentRemindingTimeLeft = True
                else:
                    if event.type == "Start":   # Agent talking starts
                        if self.isInListEltWithPattInPos(queuedEvts, "CEvtAgentSpeaking"):   # if another agent was already speaking (and has been interrupted), ends its event first
                            evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtAgentSpeaking"))
                            mtsubject.day2ExtEvents.append(Custom.CEvtAgentSpeaking(logger, evtInfos[1], event.timestamp, evtInfos[2], event.absoluteTime, evtInfos[3]))

                            """print "CEvtAgentSpeaking appending to day2ExtEvents:"
                            print "evtInfos[1] =", evtInfos[1]
                            print "event.timestamp = ", event.timestamp
                            print "evtInfos[2] = ", evtInfos[2]
                            print "event.absoluteTime = ", event.absoluteTime
                            print "evtInfos[3] = ", evtInfos[3]
                            time.sleep(3)"""

                        queuedEvts.append(["CEvtAgentSpeaking", event.timestamp, event.absoluteTime, event.agentName])
                        agentSpeaking = True

                        # Progress management phase
                        ###if not tmpIgnoreThis:
                        if event.agentName == "Mary" and event.type == "Start":
                            #AgTalk.append(str(event.scriptID) + "\t : " + str(event.text))
                            if event.scriptID in ["MaryMPTGFeedbackNeutral", "MaryMPTGAppropriateYesGoodResultsFeedback"]:
                                # when the user is done with the quiz for a subgoal, we update the goal queue
                                # Note: if he is done BUT that the results were bad (MaryMPTGAppropriateYesPoorResultsFeedback), he remains on the same subgoal
                                #print "XxXxXxXxXx " + str(goalQueue)
                                validatedSG = goalQueue.pop(0)
                                mtsubject.day2ExtEvents.append(Custom.CEvtValidatedSubgoal(logger, event.timestamp, validatedSG))
                                #print "yyyyyyyyyy " + str(goalQueue)
                                if len(goalQueue) != 0:
                                    # goalQueue[0] is for sure the current goal
                                    #print "xxx next sg in queue now pursued since quiz was successful"
                                    mtsubject.day2ExtEvents.append(Custom.CEvtPursuingNewSubgoal(logger, event.timestamp, goalQueue[0]))
                                else:
                                    # 0 codes for no current subgoal
                                    #print "xxx no sg in queue anymore after successful quiz!"
                                    mtsubject.day2ExtEvents.append(Custom.CEvtPursuingNewSubgoal(logger, event.timestamp, 0))
                            elif event.scriptID == "MaryMPTGAppropriateYesPoorResultsFeedback":
                                #print "xxx same sg in queue still pursued since quiz was not successful"
                                mtsubject.day2ExtEvents.append(Custom.CEvtPursuingSameSubgoal(logger, event.timestamp, goalQueue[0]))
                            elif event.scriptID in ["MaryMPTGAppropriateYesMediumAcceptableResultsFeedback", "MaryMPTGAppropriateYesMediumNonacceptableResultsFeedback"]:
                                mtsubject.day2ExtEvents.append(Custom.CEvtValidatedSubgoal(logger, event.timestamp, goalQueue[-1]))    # subgoal validated, even if user wants to remain on it
                                waitingForStudentInput = True
                                waitingForSGStay = True

                        # Goal setting phase
                        if event.agentName == "Pam" and event.type == "Start":
                            #AgTalk.append(str(event.scriptID) + "\t : " + str(event.text))
                            # When in the initial goal setting phase or setting up an additional goal
                            if event.scriptID == "PamSubgoalStart" or event.scriptID == "PamSubgoalStart4":     # 4 in MT 1.2.x
                                inGoalSettingPhase = True
                            # When the 3 initial goals or an additional later goal have been set up
                            elif event.scriptID in ["PamSubgoalFinished", "PamSubgoalCreated"]:
                                inGoalSettingPhase = False
                            elif event.scriptID == "PamPKAPromptBeginningSubgoal":
                                # extract the name of the current subgoal for an update of the goal queue
                                for sg in possibleSubgoalsNamesID.keys():
                                    if sg in event.text:
                                        # that subgoal should already be in the list of subgoals at least
                                        cursgid = possibleSubgoalsNamesID[sg]
                                        break
                                if cursgid not in goalQueue:
                                    logger.error("User is now working on a subgoal that isn't part of the subgoals queue")
                                else:
                                    # move the current subgoal from wherever it is to the head of the queue
                                    #if not tmpIgnoreThis:
                                    #    print "xxxxxxxxxx " + str(goalQueue)
                                    goalQueue.insert(0, goalQueue.pop(goalQueue.index(cursgid)))
                                    #if not tmpIgnoreThis:
                                    #    print "yyyyyyyyyy " + str(goalQueue)
                                    #    print "xxx new sg pursued identified thanks to pka"
                                    mtsubject.day2ExtEvents.append(Custom.CEvtPursuingNewSubgoal(logger, event.timestamp, goalQueue[0]))
                                    firstCEvtPursuingNewSubgoalAppended = True
                            elif event.scriptID == "PamPostponeSubgoalConfirm":
                                # if the user wants to postpone the subgoal, it's a good occasion to figure out the name of the current one
                                if self.isInListEltWithPattInPos(queuedEvts, "CEvtPursuingNewSubgoal"):
                                    # if there is a subgoal waiting to be identified in the queue of events, complete it and create a corresponding event
                                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtPursuingNewSubgoal"))
                                    for sg in possibleSubgoalsNamesID.keys():
                                        if sg in event.text:
                                            # that subgoal should already be in the list of subgoals at least
                                            cursgid = possibleSubgoalsNamesID[sg]
                                            break
                                    # move the current subgoal from wherever it is to the head of the queue
                                    #if not tmpIgnoreThis:
                                    #    print "xxxxxxxxxx " + str(goalQueue)
                                    goalQueue.insert(0, goalQueue.pop(goalQueue.index(cursgid)))
                                    #if not tmpIgnoreThis:
                                    #    print "yyyyyyyyyy " + str(goalQueue)
                                    #    print "xxx new sg pursued identified thanks to postpone"
                                    mtsubject.day2ExtEvents.append(Custom.CEvtPursuingNewSubgoal(logger, evtInfos[1], cursgid))
                            elif event.scriptID == "PamSubgoalTooMany": # when last setup subgoals have to be canceled
                                for g in goalsToRemove:
                                    mtsubject.day2ExtEvents.remove(g)
                                    goalCounter -= 1

                            if inGoalSettingPhase:
                                # cases where the user is asked to pick with yes/no or 1/2/3
                                if event.scriptID in ["PamSubgoalFeedbackAlmostThere", "PamSubgoalFeedback2Ideal",
                                                      "PamSubgoalFeedbackBroadSuggest", "PamSubgoalFeedbackIdealSpecific",
                                                      "PamSubgoalFeedbackManyGeneric", "PamSubgoalFeedbackManySpecific",
                                                      "PamSubgoalFeedbackPerfectIdeal", "PamSubgoalFeedbackTooSpecific",
                                                      "PamSubgoalFeedbackVagueSuggest", "PamSubgoalFeedbackSuggestRemainingSubgoals"]:
                                    waitingForGoalPick = True
                                    # get the subgoals ID from the requests
                                    sgchoices = []
                                    # in order to have the elements in the right order, they need to splitted and compared one by one to the keys
                                    # as just checking if each key is there wouldn't be enough
                                    splittext = event.text.split("'")
                                    for st in splittext:
                                        for sg in possibleSubgoalsNamesID.keys():
                                            if sg == st:
                                                sgchoices.append(sg)
                                    queuedEvts.append(["CEvtSubgoalSet", event.timestamp, sgchoices])
                                    #if not tmpIgnoreThis:
                                    #    print "ZZZZZZZZZZZZZZZZZZZZZZZ goal settings !!!! " + str(sgchoices)
                                    if waitingForStudentInput:
                                        logger.warning("Two events are waiting for a Student Input: " + event.scriptID)
                                    waitingForStudentInput = True
                                    if event.scriptID == "PamSubgoalFeedback2Ideal":
                                        # to know that there are 2 subgoals to set
                                        waitingToConfirmTwoSG = True

                        elif event.agentName == "Gavin" and event.type == "Start":
                            if event.scriptID == "GavinNewSubgoalBegin":
                                # look for the subgoal mentioned in the text of the agent
                                for sgname in possibleSubgoalsNamesID:
                                    if sgname in event.text:
                                        #sgid = possibleSubgoalsNamesID[sgname]
                                        if len(goalQueue) == 1:   # only if there were no subgoal before, and hence it's the new current one
                                            mtsubject.day2ExtEvents.append(Custom.CEvtPursuingNewSubgoal(logger, event.timestamp, goalQueue[0]))
                                        else:   # a new subgoal has been set, but we're still working on the same old one
                                            mtsubject.day2ExtEvents.append(Custom.CEvtPursuingSameSubgoal(logger, event.timestamp, goalQueue[0]))

                    elif agentSpeaking and event.type == "Stop":    # Agent talking ends
                        if agentRemindingTimeLeft:
                            # Deal with the time reminding issue separately from the rest, not to lead to confusion with a "wrong" event ID being spread
                            evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtAgentRemindsTimeLeft"))
                            mtsubject.day2ExtEvents.append(Custom.CEvtAgentRemindsTimeLeft(logger, evtInfos[1], event.timestamp, evtInfos[2], event.absoluteTime, evtInfos[3], evtInfos[4]))
                            agentRemindingTimeLeft = False

                        else:
                            evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtAgentSpeaking"))
                            mtsubject.day2ExtEvents.append(Custom.CEvtAgentSpeaking(logger, evtInfos[1], event.timestamp, evtInfos[2], event.absoluteTime, evtInfos[3]))
                            agentSpeaking = False

                            if event.scriptID in ["SamSummaryPrompt", "SamSummaryConfirm", "PamPKAPrompt", "PamPKAPromptBeginningPage", "PamPKAPromptBeginningSubgoal", "SamInfInstruction"]:
                                if waitingForStudentInput:
                                    logger.warning("Two events are waiting for a Student Input: " + event.scriptID)
                                waitingForStudentInput = True
                                if event.scriptID == "SamSummaryPrompt":        # Summary starts after agent prompt
                                    queuedEvts.append(["CEvtUserTypingSummary", event.timestamp, "agent"])
                                    waitingForEndTypingSUMM = True
                                elif event.scriptID == "SamSummaryConfirm":     # Summary starts after user's request
                                    queuedEvts.append(["CEvtUserTypingSummary", event.timestamp, "user"])
                                    waitingForEndTypingSUMM = True
                                elif event.scriptID in ["PamPKAPrompt", "PamPKAPromptBeginningPage", "PamPKAPromptBeginningSubgoal"]:   # PriorKnowledgeActivation starts
                                    queuedEvts.append(["CEvtUserTypingPKA", event.timestamp, "agent"])
                                    waitingForEndTypingPKA = True
                                elif event.scriptID == "SamInfInstruction":     # Inference starts
                                    queuedEvts.append(["CEvtUserTypingINF", event.timestamp, "user"])
                                    waitingForEndTypingINF = True

                            elif waitingForEndFirstGoals and event.scriptID == "PamSubgoalFinished":    # End of the first goals setting
                                evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger,queuedEvts, "CEvtInitialSubgoalsSetting"))
                                mtsubject.day2ExtEvents.append(Custom.CEvtInitialSubgoalsSetting(logger, evtInfos[1], event.timestamp, evtInfos[2]))
                                #if not tmpIgnoreThis:
                                #    print "xxx new sg pursued after sgsetfinished"
                                mtsubject.day2ExtEvents.append(Custom.CEvtPursuingNewSubgoal(logger, event.timestamp, goalQueue[0]))
                                waitingForEndFirstGoals = False
                                initialSubgoalsSet = True

                            elif waitingForEndNewGoal and event.scriptID == "PamSubgoalCreated":        # End of new goal setting
                                evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger,queuedEvts, "CEvtSubgoalSetting"))
                                mtsubject.day2ExtEvents.append(Custom.CEvtSubgoalSetting(logger, evtInfos[1], event.timestamp, evtInfos[2]))
                                waitingForEndNewGoal = False

                            elif waitingForPostTestReady and (event.scriptID == "GavinPresentsPretest" or event.scriptID == "GavinPresentsPretest1"):       # End of the time waiting for the post-test
                                ### FORMER LOCATION OF QUEUE CLEANING - moved to "PostTestIntro" event to clean earlier
                                evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger,queuedEvts, "CEvtUserWaitingForPostTest"))
                                mtsubject.day2ExtEvents.append(Custom.CEvtUserWaitingForPostTest(logger, evtInfos[1], event.timestamp, evtInfos[2]))
                                # add an estimated time of view for the last page viewed
                                if prevPageInView != "":
                                    prevPageInView.timeSpentOverall = event.timestamp - prevPageInView.timestamp
                                    prevPageInView.timeSpentWithContent = prevPageInView.timeSpentOverall - (timeQuestionnairePaused + timeSystemPaused + timeVideoPaused)      # also substract time spent on questionnaires, watching videos and system pauses, as it's not time spent reading
                                waitingForPostTestReady = False

                            elif event.scriptID == "GavinPresentsPretest2": # Wait for the next student input that will determine when the user starts taking the posttest
                                waitingForPostTestStart = True
                                waitingForStudentInput = True

                            elif waitingForPostTestEnd and event.scriptID == "Posttest finished":     # User has finished the posttest
                                evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger,queuedEvts, "CEvtUserTakingPostTest"))
                                try:
                                    eventQuizElements = evtInfos[3]
                                except IndexError:
                                    eventQuizElements = []
                                    logger.warning("A queued CEvtUserTakingPostTest event doesn't have any quiz element associated to it")
                                mtsubject.day2ExtEvents.append(Custom.CEvtUserTakingPostTest(logger, evtInfos[1], event.timestamp, evtInfos[2], eventQuizElements))
                                waitingForPostTestEnd = False

            elif isinstance(event, Dialog.MTDialogUserEvent):                         ### TYPE 3
                if waitingForStudentInput:  # Current duration event ended by the user input being submitted
                    waitingForStudentInput = False
                    if waitingForSummaryAdditionToNotes: # when waiting to know if the user wants to add typed summary to notes
                        waitingForSummaryAdditionToNotes = False
                        if event.input != "Yes":    # if not, we'll count properly the next time Notes layout appear
                            mtsubject.day2ExtEvents.append(Custom.CEvtNoteNotAddedFromSummary(logger, event.timestamp))
                        else:   # if yes, we add a special event and will ignore the brief opening of the Notes layout
                            mtsubject.day2ExtEvents.append(Custom.CEvtNoteAddedFromSummary(logger, event.timestamp))

                    elif waitingForDependsValue:  # Retrieve the SRL event related to the answer to a DEPENDS
                        waitingForDependsValue = False
                        if len(queuedDepends) != 1:
                            logger.warning("Several Depends events are waiting to be analyzed, which shouldn't happen")
                        try:
                            evt = queuedDepends.pop(0)
                        except IndexError:
                            logger.error("No DEPENDS event in the queue")
                            raise
                        evt.setRealSRLType(logger, event.input)

                    elif waitingForPostpone:    # the answer will mean the subgoal is postponed or not
                        waitingForPostpone = False
                        evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger,queuedEvts, "CEvtPostponingSubgoal"))
                        if event.input == "Yes":
                            #if not tmpIgnoreThis:
                            #    print "xxx new sg pursued after postpone, but we don't know which one"
                            mtsubject.day2ExtEvents.append(Custom.CEvtPostponingSubgoal(logger, evtInfos[1], event.timestamp, evtInfos[2]))
                            # update the goal queue
                            #goalQueue.append(goalQueue.pop(0))  not here, as we don't know the new one yet
                            #mtsubject.day2ExtEvents.append(Custom.CEvtPursuingNewSubgoal(logger, event.timestamp, 0))
                            queuedEvts.append(["CEvtPursuingNewSubgoal", event.timestamp, -1])
                            # -1 for unknown subgoal
                        elif event.input == "No":
                            mtsubject.day2ExtEvents.append(Custom.CEvtNotPostponingSubgoal(logger, evtInfos[1], event.timestamp, evtInfos[2]))
                        else:
                            logger.warning("Unknown kind of student input in answer to a postpone subgoal confirmation: " + event.input)

                    elif waitingForSGStay:
                        waitingForSGStay = False
                        if event.input == "No": # move on to the next subgoal
                            goalQueue.pop(0)
                            if len(goalQueue) != 0:   # goalQueue[0] is for sure the current goal
                                #print "User is ok to move on subgoal after successful quiz - go to the next one"
                                mtsubject.day2ExtEvents.append(Custom.CEvtPursuingNewSubgoal(logger, event.timestamp, goalQueue[0]))
                            else:
                                #print "User is ok to move on subgoal after successful quiz - no subgoals left in stack"
                                mtsubject.day2ExtEvents.append(Custom.CEvtPursuingNewSubgoal(logger, event.timestamp, 0))    # 0 codes for no current subgoal
                        elif event.input == "Yes": # stay on the current subgoal
                            #print "User stays on subgoal despite successful quiz"
                            mtsubject.day2ExtEvents.append(Custom.CEvtPursuingSameSubgoal(logger, event.timestamp, goalQueue[0]))
                        else:
                            logger.warning("Unknown kind of student input in answer to a question to stay on their current subgoal: " + event.input)

                    elif waitingForCE:          # user is evaluating the content
                        waitingForCE = False
                        evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserEvaluatingContentCE"))
                        mtsubject.day2ExtEvents.append(Custom.CEvtUserEvaluatingContentCE(logger, evtInfos[1], event.timestamp, event.input, evtInfos[2]))
                    elif waitingForMPTG:        # user has been prompted or decided to finish a subgoal
                        waitingForMPTG = False
                        evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserMovingTowardGoalMPTG"))
                        if event.input == "Yes":
                            mtsubject.day2ExtEvents.append(Custom.CEvtUserMovingTowardGoalMPTG(logger, evtInfos[1], event.timestamp, evtInfos[2]))
                        elif event.input == "No":
                            mtsubject.day2ExtEvents.append(Custom.CEvtUserNotMovingTowardGoalMPTG(logger, evtInfos[1], event.timestamp, evtInfos[2]))
                        else:
                            logger.warning("Unknown kind of student input in answer to MPTG: " + event.input)

                    elif waitingForJOL:         # user has been prompted or decided to judge his current learning
                        waitingForJOL = False
                        evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserJudgingLearningJOL"))
                        mtsubject.day2ExtEvents.append(Custom.CEvtUserJudgingLearningJOL(logger, evtInfos[1], event.timestamp, event.input, evtInfos[2]))

                    elif waitingForFOK:         # user has been prompted or decided to tell how much he knows of a topic
                        waitingForFOK = False
                        evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserFeelingKnowledgeFOK"))
                        mtsubject.day2ExtEvents.append(Custom.CEvtUserFeelingKnowledgeFOK(logger, evtInfos[1], event.timestamp, event.input, evtInfos[2]))

                    elif waitingForEndTypingPKA:# user has typed prior knowledge
                        waitingForEndTypingPKA = False
                        evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTypingPKA"))
                        try:
                            typingEvt = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "RulePKAorINForSUMM", reportError=False))[1]
                        except ValueError:   # when the PKA was triggered but not because of a rule (initial one for the circulatory system)
                            typingEvt = None
                        mtsubject.day2ExtEvents.append(Custom.CEvtUserTypingPKA(logger, evtInfos[1], event.timestamp, evtInfos[2], typingEvt))
                        #bondaria
                        #calculate duration of reporting prior knowledge
                        if startedBrowsing:
                            durationSRL  += event.timestamp - evtInfos[1]
                        #---------
                    elif waitingForEndTypingINF:
                        waitingForEndTypingINF = False
                        evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTypingINF"))
                        typingEvt = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "RulePKAorINForSUMM", reportError=False))[1]
                        mtsubject.day2ExtEvents.append(Custom.CEvtUserTypingINF(logger, evtInfos[1], event.timestamp, evtInfos[2], typingEvt))
                        #bondaria
                        #calculate duration of reporting prior knowledge
                        if startedBrowsing:
                            durationSRL  += event.timestamp - evtInfos[1]
                        #---------
                    elif waitingForEndTypingSUMM:
                        waitingForEndTypingSUMM = False
                        evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTypingSummary"))
                        typingEvt = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "RulePKAorINForSUMM", reportError=False))[1]
                        mtsubject.day2ExtEvents.append(Custom.CEvtUserTypingSummary(logger, evtInfos[1], event.timestamp, evtInfos[2], typingEvt))
                        #bondaria
                        #calculate duration of reporting prior knowledge
                        if startedBrowsing:
                            durationSRL  += event.timestamp - evtInfos[1]
                        #---------
                    elif waitingForPostTestStart:    # user is starting the posttest
                        waitingForPostTestStart = False
                        waitingForPostTestEnd = True
                        queuedEvts.append(["CEvtUserTakingPostTest", event.timestamp, event])

                    elif waitingForGoalPick:
                        waitingForGoalPick = False
                        evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtSubgoalSet"))
                        #if not tmpIgnoreThis:
                        #    print "zzzzzzzzzzzzzzz " + str(event.input) + "  " + str(evtInfos[2])
                        if event.input == "Yes":
                            if len(evtInfos[2]) != 1:
                                if waitingToConfirmTwoSG and len(evtInfos[2]) == 2:
                                    waitingToConfirmTwoSG = False
                                    goalCounter += 2
                                    newevt1 = Custom.CEvtSubgoalSet(logger, evtInfos[1], goalCounter, evtInfos[2][0], possibleSubgoalsNamesID[evtInfos[2][0]])
                                    mtsubject.day2ExtEvents.append(newevt1)
                                    #if not tmpIgnoreThis:
                                    #    print "xxxxxxxxxx " + str(goalQueue)
                                    goalQueue.append(possibleSubgoalsNamesID[evtInfos[2][0]])
                                    newevt2 = Custom.CEvtSubgoalSet(logger, evtInfos[1], goalCounter, evtInfos[2][1], possibleSubgoalsNamesID[evtInfos[2][1]])
                                    mtsubject.day2ExtEvents.append(newevt2)
                                    goalQueue.append(possibleSubgoalsNamesID[evtInfos[2][1]])
                                    # if goals need to be removed later on, in case we are above the 3 subgoals to set
                                    goalsToRemove.append(newevt1)
                                    goalsToRemove.append(newevt2)
                                    #if not tmpIgnoreThis:
                                    #    print "yyyyyyyyyy " + str(goalQueue)
                                else:
                                    logger.warning("Several subgoals found associated to a yes/no answer for a goal setting: " + str(evtInfos[2]))
                            else:
                                mtsubject.day2ExtEvents.append(Custom.CEvtSubgoalSet(logger, evtInfos[1], goalCounter, evtInfos[2][0], possibleSubgoalsNamesID[evtInfos[2][0]]))
                                goalCounter += 1
                                # update the goal queue
                                #if not tmpIgnoreThis:
                                #    print "xxxxxxxxxx " + str(goalQueue)
                                goalQueue.append(possibleSubgoalsNamesID[evtInfos[2][0]])
                                #if not tmpIgnoreThis:
                                #    print "yyyyyyyyyy " + str(goalQueue)
                                #mtsubject.day2ExtEvents.append(Custom.CEvtPursuingNewSubgoal(logger, event.timestamp, goalQueue[0]))
                        elif event.input in ["1", "2", "3", "4"]:
                            if len(evtInfos[2]) < int(event.input):
                                if int(event.input) == len(evtInfos[2]) + 1:
                                    # there are sometimes cases where for one option only, what is shown is not yes/no but the option/None (which is worth 2 if selected)
                                    # there are also cases where 3 options + None are shown, then 4 means None and should be considered like a "No" to a yes/no question
                                    pass
                                else:
                                    logger.error("Answer to a goal setting event is out of boundaries: " + event.input)
                            else:
                                mtsubject.day2ExtEvents.append(Custom.CEvtSubgoalSet(logger, evtInfos[1], goalCounter, evtInfos[2][int(event.input) - 1], possibleSubgoalsNamesID[evtInfos[2][int(event.input) - 1]]))
                                goalCounter += 1
                                # update the goal queue
                                #if not tmpIgnoreThis:
                                #    print "xxxxxxxxxx " + str(goalQueue)
                                goalQueue.append(possibleSubgoalsNamesID[evtInfos[2][int(event.input) - 1]])
                                #if not tmpIgnoreThis:
                                #    print "yyyyyyyyyy " + str(goalQueue)
                                #mtsubject.day2ExtEvents.append(Custom.CEvtPursuingNewSubgoal(logger, event.timestamp, goalQueue[0]))
                        elif event.input != "No" and event.input != "0":
                            logger.error("Unknown answer to a goal setting event: " + event.input)
                    else:
                        logger.warning("Student Input that couldn't be related to any ongoing event: " + event.input)

                else:
                    logger.debug("Student Input ignored: " + event.input)
                    pass

            elif isinstance(event, Dialog.MTDialogAgentEvent):                     ### TYPE 3
                if event.scriptID == "GavinIntroEnd":   # the intro ends, ignore the time spent watching videos and answering questionnaires before that, so it doesn't negatively affect the time spent on the very first page
                    timeVideoPaused = datetime.timedelta(0, 0, 0)
                    timeQuestionnairePaused = datetime.timedelta(0, 0, 0)
                    timeSystemPaused = datetime.timedelta(0, 0, 0)
                elif event.scriptID == "SamSUMFeedbackNeutral" or event.scriptID == "FeedbackSumGood":   # when Sam asks to add notes to summary
                    # if the users accepts, it will briefly open the Notes layout
                    # but in that case, this layout change should be ignored as the beginning of an event where a user takes note
                    waitingForSummaryAdditionToNotes = True
                    waitingForStudentInput = True

            elif isinstance(event, Quiz.MTQuizEvent):                               ### TYPE 4
                if not (waitingForEndQuiz or waitingForPostTestEnd):
                    logger.warning("A quiz question is happening out of the context of any quiz: " + str(event.getInfo(showAll=True)))       # it shouldn't happen
                elif waitingForEndQuiz:
                    # add the quiz event to the CEvtUserTakingQuiz event under construction
                    idxQuiz = self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTakingQuiz")
                    if len(queuedEvts[idxQuiz]) == 4:        # if it's the first one
                        queuedEvts[idxQuiz].append([event])
                    elif len(queuedEvts[idxQuiz]) == 5:     # if some have already been added
                        queuedEvts[idxQuiz][4].append(event)
                    else:
                        logger.warning("A queued CEvtUserTakingQuiz had a length of " + str(len(queuedEvts[idxQuiz])) + "instead of 4 or 5: " + str(queuedEvts[idxQuiz]))
                else:
                    # add the quiz event to the CEvtUserTakingPostTest event under construction
                    idxQuiz = self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTakingPostTest")
                    if len(queuedEvts[idxQuiz]) == 3:        # if it's the first one
                        queuedEvts[idxQuiz].append([event])
                    elif len(queuedEvts[idxQuiz]) == 4:     # if some have already been added
                        queuedEvts[idxQuiz][3].append(event)
                    else:
                        logger.warning("A queued CEvtUserTakingPostTest had a length of " + str(len(queuedEvts[idxQuiz])) + "instead of 3 or 4: " + str(queuedEvts[idxQuiz]))

            elif isinstance(event, Layout.MTLayoutEvent):                          ### TYPE 7
                if systemPaused:
                    systemPaused = False
                    timeSystemPaused = event.timestamp - timeSystemPaused   # evaluate the time spent in pause
                if videoPaused:
                    videoPaused = False
                    #timeVideoPaused = event.timestamp - timeVideoPaused    # evaluate the time spent watching the video
                    #bondaria-----
                    #this fix is required if VideoTutorial pops up during taking quiz
                    if waitingForEndQuiz: #if Quiz is now on, video duration is already taken into account
                        timeVideoPaused = datetime.timedelta(0,0,0)
                    else:
                        timeVideoPaused = event.timestamp - timeVideoPaused    # evaluate the time spent watching the video

                    #---
                if waitingForEndQuiz and (event.layout == "InputWithContent" or event.layout == "Normal" or event.layout == "InputNoContent"):    # Page Quiz ends
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTakingQuiz"))
                    try:
                        eventQuizElements = evtInfos[4]
                    except IndexError:
                        eventQuizElements = []
                        logger.warning("A queued CEvtUserTakingQuiz event doesn't have any quiz element associated to it (" + str(evtInfos[1]) + str(evtInfos[2]) + ")")
                    mtsubject.day2ExtEvents.append(Custom.CEvtUserTakingQuiz(logger, evtInfos[1], event.timestamp, evtInfos[2], evtInfos[3], eventQuizElements))
                    #bondaria
                    #calculate duration of Quiz
#                    if startedBrowsing:
#                        print "**************"
#                        print "Duration: ", durationQuiz
#                        print "Finish: ", event.timestamp
#                        print "Start: ", evtInfos[1]
#                        durationQuiz  += event.timestamp - evtInfos[1]
#                        print "Duration: ", durationQuiz
#                        print "**************"
#
#                    #---------
                    waitingForEndQuiz = False

                elif event.layout == "TutorialVideo":
                    videoPaused = True
                    #timeVideoPaused = event.timestamp
                    #bondaria
                    if waitingForEndQuiz: #if Quiz is now on, video duration is already taken into account
                        timeVideoPaused = datetime.timedelta(0,0,0)
                    else:
                        timeVideoPaused = event.timestamp

                    #--- this fix is required if VideoTutorial pops up during taking quiz
                elif event.layout == "Pause":
                    systemPaused = True
                    timeSystemPaused = event.timestamp

                elif event.layout == "Notes":  # User starts taking notes
                    if not waitingForSummaryAdditionToNotes:
                        if self.isInListEltWithPattInPos(queuedEvts, "CEvtNoteTakeGUI"):
                            logger.warning("Two note taking events are claimed to be taking place at the same time")
                        queuedEvts.append(["CEvtNoteTakeGUI", event.timestamp])
                        waitingForEndNotes = True
                elif event.layout != "Notes":
                    if waitingForEndNotes:
                        # Apparently the user wasn't taking notes but reading them, OR he got interrupted by the agent
                        # we need to replace the event stored in queue
                        if waitingForStudentInput:
                            evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtNoteTakeGUI"))
                            try:    # if a TN rule has been triggered before, associate it to this event
                                evtTN = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "MTRuleTNEvent"))[1]
                            except ValueError:
                                evtTN = None
                            mtsubject.day2ExtEvents.append(Custom.CEvtNoteTakeGUI(logger, evtInfos[1], event.timestamp, True, None, evtTN))
                            # don't stop waitingForStudentInput, because it's related to another event
                        else:
                            evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtNoteTakeGUI"))
                            try:    # if a TN rule has been triggered before, associate it to this event
                                evtTN = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "MTRuleTNEvent", reportError=False))[1]
                            except ValueError:
                                evtTN = None
                            mtsubject.day2ExtEvents.append(Custom.CEvtNoteCheckGUI(logger, evtInfos[1], event.timestamp, evtTN))
                        waitingForEndNotes = False

            elif waitingForEndNotes and isinstance(event, Notes.MTNoteEvent):      ### TYPE 5
                # User has finished taking notes
                evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtNoteTakeGUI"))
                try:    # if a TN rule has been triggered before, associate it to this event
                    evtTN = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "MTRuleTNEvent"))[1]
                except ValueError:
                    evtTN = None
                mtsubject.day2ExtEvents.append(Custom.CEvtNoteTakeGUI(logger, evtInfos[1], event.timestamp, False, event.pageID, evtTN))
                waitingForEndNotes = False

            elif True in [isinstance(event, evtType) for evtType in [Rule.MTRulePKAEvent, Rule.MTRuleINFEvent, Rule.MTRuleSUMMEvent]]:      ### TYPE 2
                # those events are saved to be associated to the custom events that are going to be created based on the associated agent script - memorize them for now
                queuedEvts.append(["RulePKAorINForSUMM", event])

            elif isinstance(event, Rule.MTRuleTNEvent):                             ### TYPE 2
                queuedEvts.append(["MTRuleTNEvent", event])

            elif isinstance(event, Rule.MTRuleQuizEvent):                          ### TYPE 2
                # Page Quiz starts
                if self.isInListEltWithPattInPos(queuedEvts, "CEvtUserTakingQuiz"):
                    logger.warning("Two quizzes are claimed to be taking place at the same time")
                if event.about == "page":
                    queuedEvts.append(["CEvtUserTakingQuiz", event.timestamp, event.contentIdx, None])
                elif event.about == "subgoal":
                    queuedEvts.append(["CEvtUserTakingQuiz", event.timestamp, None, event.contentIdx])
                    # it is also a good occasion to set up the ID of the subgoal that was ongoing, if it's not known
                    ###if not tmpIgnoreThis:
                    if self.isInListEltWithPattInPos(queuedEvts, "CEvtPursuingNewSubgoal"):
                        # if there is a subgoal waiting to be identified in the queue of events, complete it and create a corresponding event
                        evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtPursuingNewSubgoal"))
                        #print "xxx new sg pursued identified thanks to quiz"
                        mtsubject.day2ExtEvents.append(Custom.CEvtPursuingNewSubgoal(logger, evtInfos[1], int(event.contentIdx)))
                        # move the current subgoal from wherever it is to the head of the queue
                        goalQueue.insert(0, goalQueue.pop(goalQueue.index(int(event.contentIdx))))
                else:
                    logger.warning("Unknown purpose of a quiz: " + event.about)
                waitingForEndQuiz = True

            elif isinstance(event, Rule.MTRuleFlowCantStart):                      ### TYPE 2
                # delete the latest waiting events
                queuedEvts = queuedEvts[:-1]
                # need to cancel the latest SRL event
                if event.eventToCancel == "CE":
                    waitingForCE = False
                elif event.eventToCancel == "FOK":
                    waitingForFOK = False
                elif event.eventToCancel == "JOL":
                    waitingForJOL = False
                elif event.eventToCancel == "MPTG":
                    waitingForMPTG = False
                else:
                    # RR, COIS don't wait for any input
                    # PLAN, SUMM, TN, PKA, INF not considered
                    pass
                # if there is no other event waiting for a student input, it was certainly caused by the element just discarded
                if not (waitingForCE or waitingForDependsValue or waitingForEndNotes or waitingForFOK or waitingForJOL or waitingForMPTG):
                    waitingForStudentInput = False

            elif isinstance(event, Rule.MTRuleSRLEvent):                           ### TYPE 2
                # SRL Event starts
                # Checks if the event is of one of the classes given in the list
                if True in list(map(lambda evtClass:isinstance(event, evtClass), [Rule.MTRuleMPTGEvent, Rule.MTRuleJOLEvent,
                                                                            Rule.MTRuleFOKEvent, Rule.MTRuleCEEvent,
                                                                            Rule.MTRuleDependsEvent])):
                    # Check if there is already another event waiting for a student input (which shouldn't be the case)
                    if waitingForStudentInput:
                        logger.warning("Two events are waiting for a Student Input: " + event.rule)
                    waitingForStudentInput = True

                    if isinstance(event, Rule. MTRuleMPTGEvent):   # Request to know progress towards goal
                        # the set on the right is *NOT* the keys of MPTGrules (as one element there is punctual)
                        if event.trigger != "too early": # when it's too early, the agent isn't waiting for a reaction from the user
                            if event.rule in ["User MPTG appropriate", "Prompt MPTG on time limit", "Prompt MPTG on percent complete"]:
                                waitingForMPTG = True
                                queuedEvts.append(["CEvtUserMovingTowardGoalMPTG", event.timestamp, event])
                        else:
                            waitingForStudentInput = False

                    elif isinstance(event, Rule.MTRuleJOLEvent):   # Request to judge the learning
                        if event.rule in event.JOLrules.keys():
                            waitingForJOL = True
                            queuedEvts.append(["CEvtUserJudgingLearningJOL", event.timestamp, event])

                    elif isinstance(event, Rule.MTRuleFOKEvent):   # Request to evaluate the feeling of knowing
                        if event.startingAction != "":  # when it's empty, it means it's not a FOK waiting for an answer
                            if event.rule in event.FOKrules.keys():
                                waitingForFOK = True
                                queuedEvts.append(["CEvtUserFeelingKnowledgeFOK", event.timestamp, event])
                        else:
                            waitingForStudentInput = False

                    elif isinstance(event, Rule.MTRuleCEEvent):   # Request to evaluate the content of a page
                        if event.startingAction != "":  # when it's empty, it means it's not a FOK waiting for an answer
                            if event.startingAction in event.CEstartingActions.keys():
                                waitingForCE = True
                                queuedEvts.append(["CEvtUserEvaluatingContentCE", event.timestamp, event])
                        else:
                            waitingForStudentInput = False

                    elif isinstance(event, Rule.MTRuleDependsEvent):   # Request to judge the learning
                        waitingForDependsValue = True
                        queuedDepends.append(event)

                elif isinstance(event, Rule.MTRulePLANEvent):   # Planification starts
                    if event.startingAction == "start":                     # beginning of the program
                        if waitingForEndFirstGoals:
                            logger.warning("Two events are waiting for the end of first goals planification")
                        waitingForEndFirstGoals = True
                        queuedEvts.append(["CEvtInitialSubgoalsSetting", event.timestamp, event])

                    elif event.startingAction == "PostTestIntro":           # user requests the post-test, and needs to wait for the experimenter to type a password
                        # when the posttest starts, any action that was waiting for a student input should be ignored
                        (agentSpeaking, agentRemindingTimeLeft, waitingForStudentInput,
                         waitingForEndQuiz, waitingForEndNotes, waitingForDependsValue,
                         waitingForEndFirstGoals, waitingForEndNewGoal, waitingForPostTestReady,
                         waitingForPostTestStart, waitingForPostTestEnd, waitingForPostpone,
                         waitingForSummaryAdditionToNotes, waitingForCE, waitingForMPTG,
                         waitingForJOL, waitingForFOK, waitingForEndTypingPKA,
                         waitingForEndTypingINF, waitingForEndTypingSUMM, waitingForVideoEnd
                         ) = (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
                        # keep only elements not interrupted by the transition to the posttest
                        # (i.e. the event relative to the posttest itself and note taken on paper (cf. 23031))
                        cleanQueue = []
                        for evt in queuedEvts:
                            if evt[0] in ["CEvtUserWaitingForPostTest", "CEvtNoteTakenOnPaper"]:
                                cleanQueue.append(evt)
                        queuedEvts = cleanQueue
                        queuedDepends = []
                        if waitingForPostTestReady:
                            logger.warning("Two events are waiting for the start of the post-test")
                        waitingForPostTestReady = True
                        queuedEvts.append(["CEvtUserWaitingForPostTest", event.timestamp, event])

                    elif event.startingAction == "AskIfPostponeSubgoal":    # user requests to postpone the current subgoal
                        if waitingForStudentInput:
                            logger.warning("Two events are waiting for a Student Input: " + event.rule)
                        waitingForStudentInput = True
                        waitingForPostpone = True
                        queuedEvts.append(["CEvtPostponingSubgoal", event.timestamp, event])

                    elif event.startingAction == "SuggestAddNewSubgoal":    # agent prompts possibility for a new subgoal
                        mtsubject.day2ExtEvents.append(Custom.CEvtSubgoalSuggested(logger, event.timestamp))

                    elif event.startingAction == "newSubgoal":              # new subgoal
                        if waitingForEndNewGoal:
                            logger.warning("Two new subgoals are being set at the same time")
                        waitingForEndNewGoal = True
                        queuedEvts.append(["CEvtSubgoalSetting", event.timestamp, event])

                    else:
                        logger.warning("Unknown kind of PLAN: " + event.startingAction)

        queuedEvts2 = []
        if stopTimeStamp == None:
            for evt in queuedEvts:
                if not (evt[0] == "CEvtNoteTakenOnPaper" and mtsubject.ID in mtsubject.checkedIDsForPenOnAtTheEnd):
                    queuedEvts2.append(evt)
            if (queuedEvts2 != []):
                logger.warning("List of remaining queued events for day 2 (should be empty): " + str(queuedEvts))
        else:
            """--------------------------------NJ: CODE TO DEAL WITH STOP TIME STAMP--------------------------------------"""
            for evt in queuedEvts:
                if evt[0] == "CEvtVideoIsPlaying":
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtVideoIsPlaying"))
                    mtsubject.day2ExtEvents.append(Custom.CEvtVideoIsPlaying(logger, evtInfos[1], stopTimeStamp, evtInfos[2]))
                    waitingForVideoEnd = False
                elif evt[0] == "CEvtQuestionnaireOngoing":
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtQuestionnaireOngoing"))
                    mtsubject.day2ExtEvents.append(Custom.CEvtQuestionnaireOngoing(logger, evtInfos[1], stopTimeStamp, evtInfos[2]))
                    waitingForQuestionnaireEnd = False
                    timeQuestionnairePaused = stopTimeStamp - timeQuestionnairePaused   # the timer ends being paused
                    timeQuestionnairePaused += timePreviousQuestionnairePaused      # add time from a previous questionnaire while being on the same page, if any
                    timePreviousQuestionnairePaused = datetime.timedelta(0, 0, 0)
                elif evt[0] == "CEvtNoteTakenOnPaper":
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtNoteTakenOnPaper"))
                    mtsubject.day2ExtEvents.append(Custom.CEvtNoteTakenOnPaper(logger, evtInfos[1], stopTimeStamp))
                    waitingForPenEnd = False
                elif evt[0] == "CEvtAgentRemindsTimeLeft":
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtAgentRemindsTimeLeft"))
                    diff = stopTimeStamp - evtInfos[1]
                    absoluteTime = evtInfos[2] + diff
                    mtsubject.day2ExtEvents.append(Custom.CEvtAgentRemindsTimeLeft(logger, evtInfos[1], stopTimeStamp, evtInfos[2], absoluteTime, evtInfos[3], evtInfos[4]))
                    agentRemindingTimeLeft = False
                elif evt[0] == "CEvtAgentSpeaking":
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtAgentSpeaking"))
                    diff = stopTimeStamp - evtInfos[1]
                    absoluteTime = evtInfos[2] + diff
                    mtsubject.day2ExtEvents.append(Custom.CEvtAgentSpeaking(logger, evtInfos[1], stopTimeStamp, evtInfos[2], absoluteTime, evtInfos[3]))
                    agentSpeaking = False
                elif evt[0] == "CEvtUserTypingSummary":
                    waitingForEndTypingSUMM = False
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTypingSummary"))
                    typingEvt = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "RulePKAorINForSUMM", reportError=False))[1]
                    mtsubject.day2ExtEvents.append(Custom.CEvtUserTypingSummary(logger, evtInfos[1], stopTimeStamp, evtInfos[2], typingEvt))
                    #bondaria
                    #calculate duration of reporting prior knowledge
                    if startedBrowsing:
                        durationSRL  += stopTimeStamp - evtInfos[1]
                elif evt[0] == "CEvtUserTypingPKA":
                    waitingForEndTypingPKA = False
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTypingPKA"))
                    try:
                        typingEvt = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "RulePKAorINForSUMM", reportError=False))[1]
                    except ValueError:   # when the PKA was triggered but not because of a rule (initial one for the circulatory system)
                        typingEvt = None
                    mtsubject.day2ExtEvents.append(Custom.CEvtUserTypingPKA(logger, evtInfos[1], stopTimeStamp, evtInfos[2], typingEvt))
                    #bondaria
                    #calculate duration of reporting prior knowledge
                    if startedBrowsing:
                        durationSRL  += stopTimeStamp - evtInfos[1]
                elif evt[0] == "CEvtUserTypingINF":
                    waitingForEndTypingINF = False
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTypingINF"))
                    typingEvt = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "RulePKAorINForSUMM", reportError=False))[1]
                    mtsubject.day2ExtEvents.append(Custom.CEvtUserTypingINF(logger, evtInfos[1], stopTimeStamp, evtInfos[2], typingEvt))
                    #bondaria
                    #calculate duration of reporting prior knowledge
                    if startedBrowsing:
                        durationSRL  += stopTimeStamp - evtInfos[1]
                elif evt[0] == "CEvtInitialSubgoalsSetting":
                    pass #Don't have to deal with this because loop can't exit before this is finished
                elif evt[0] == "CEvtSubgoalSetting":
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger,queuedEvts, "CEvtSubgoalSetting"))
                    mtsubject.day2ExtEvents.append(Custom.CEvtSubgoalSetting(logger, evtInfos[1], stopTimeStamp, evtInfos[2]))
                    waitingForEndNewGoal = False
                elif evt[0] == "CEvtPursuingNewSubgoal":
                    pass #Can't add what goal it is until they pick it
                elif evt[0] == "CEvtPostponingSubgoal":
                    pass #Can't add because we don't know if they respond 'yes' or 'no' to postponing subgoal
                elif evt[0] == "CEvtSubgoalSet":
                    pass #can't add because they could be considering multiple subgoals and we don't know which one they want to choose without their answer
                elif evt[0] == "CEvtUserWaitingForPostTest":
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger,queuedEvts, "CEvtUserWaitingForPostTest"))
                    mtsubject.day2ExtEvents.append(Custom.CEvtUserWaitingForPostTest(logger, evtInfos[1], stopTimeStamp, evtInfos[2]))
                    # add an estimated time of view for the last page viewed
                    if prevPageInView != "":
                        prevPageInView.timeSpentOverall = stopTimeStamp - prevPageInView.timestamp
                        prevPageInView.timeSpentWithContent = prevPageInView.timeSpentOverall - (timeQuestionnairePaused + timeSystemPaused + timeVideoPaused)      # also substract time spent on questionnaires, watching videos and system pauses, as it's not time spent reading
                    waitingForPostTestReady = False
                elif evt[0] == "CEvtUserTakingPostTest":
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger,queuedEvts, "CEvtUserTakingPostTest"))
                    try:
                        eventQuizElements = evtInfos[3]
                    except IndexError:
                        eventQuizElements = []
                        logger.warning("A queued CEvtUserTakingPostTest event doesn't have any quiz element associated to it")
                    mtsubject.day2ExtEvents.append(Custom.CEvtUserTakingPostTest(logger, evtInfos[1], stopTimeStamp, evtInfos[2], eventQuizElements))
                    waitingForPostTestEnd = False
                elif evt[0] == "CEvtUserEvaluatingContentCE":
                    #This event relates to the user clicking a button that says "Evaluate how well this relates to my current subgoal"
                    #They can click whether the 'Page', 'Image', 'Both', or 'None' relate to the subgoal
                    #Without knowing event.input (aka whether they select 'page', 'image', etc.) we basically can't count this
                    """waitingForCE = False
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserEvaluatingContentCE"))
                    mtsubject.day2ExtEvents.append(Custom.CEvtUserEvaluatingContentCE(logger, evtInfos[1], stopTimeStamp, event.input, evtInfos[2]))"""
                    pass
                elif evt[0] == "CEvtUserMovingTowardGoalMPTG":
                    #For similar reasons to Evaluating Content above, without knowing whether the user chooses 'yes' or 'no' as an answer
                    #we can't append this event
                    pass
                elif evt[0] == "CEvtUserJudgingLearningJOL":
                    #same as above, can't append without input
                    pass
                elif evt[0] == "CEvtUserFeelingKnowledgeFOK":
                    #same as above, can't append without input
                    pass
                elif evt[0] == "RulePKAorINForSUMM":
                    #does not itself get added to day 2 events, but is processed as part of other events
                    pass
                elif evt[0] == "CEvtUserTakingQuiz":
                    evtInfos = queuedEvts.pop(self.getIdxOfLastListEltWithPattInPos(logger, queuedEvts, "CEvtUserTakingQuiz"))
                    try:
                        eventQuizElements = evtInfos[4]
                    except IndexError:
                        eventQuizElements = []
                        logger.warning("A queued CEvtUserTakingQuiz event doesn't have any quiz element associated to it (" + str(evtInfos[1]) + str(evtInfos[2]) + ")")
                    mtsubject.day2ExtEvents.append(Custom.CEvtUserTakingQuiz(logger, evtInfos[1], stopTimeStamp, evtInfos[2], evtInfos[3], eventQuizElements))
                    waitingForEndQuiz = False
                elif evt[0] == "CEvtNoteTakeGUI":
                    pass
                elif evt[0] == "MTRuleTNEvent":
                    pass

                """--------------------------------END CODE TO DEAL WITH STOP TIME STAMP--------------------------------------"""

        # Make a chronological list of ALL events for day 2, not to have to fusionate them all the time for that
        mtsubject.day2AllEvents = list(mtsubject.day2Events)              # make a copy of the original events list
        mtsubject.day2AllEvents.extend(mtsubject.day2ExtEvents)       # add the extended events to the copy
        mtsubject.day2AllEvents.sort(key=lambda t: (t.getTimeStart().hour, t.getTimeStart().minute, t.getTimeStart().second, t.getTimeStart().microsecond))

        """for evt in list(mtsubject.day2ExtEvents):
            print evt.getInfo()
        time.sleep(60)
        X = list(mtsubject.day2ExtEvents)
        print X[-1]"""

    def makeSubtitles(self, logger, mtsubject, offsetMode=0):
        #: list of subtitles, formatted as [id, [timestampStart, timestampEnd], content]
        subs = []
        #: use an offset (if defined for this subject) to get into the video time referential
        offset = datetime.timedelta(seconds=mtsubject.timeOffset[offsetMode])
        #: time for the subtitles to be displayed if they are punctual events
        defaultDuration = datetime.timedelta(seconds=5)

        # Retrieve some punctual events from the day2Events list (the ones not used to build extended custom events)
        for event in mtsubject.day2Events:
            for eventToSubtitle in [Browsing.MTBrowsingPageEvent, Browsing.MTBrowsingImageEvent,
                                    Quiz.MTQuizEvent,
                                    Rule.MTRuleSUMMEvent, Rule.MTRulePKAEvent, Rule.MTRuleINFEvent,
                                    Rule.MTRuleTNEvent, Rule.MTRuleDependsEvent,
                                    Rule.MTRuleRREvent, Rule.MTRuleCOISEvent]:
                if isinstance(event, eventToSubtitle):
                    if event.sub == "":
                        logger.warning("There is an empty subtitle")
                    else:
                        subs.append([event.timestamp + offset, event.timestamp + offset + defaultDuration, event.styleStart + event.sub + event.styleEnd])
        # Retrieve all the events from the extended events list
        for event in mtsubject.day2ExtEvents:
            if event.punctual:  # for punctual events, we make the subtitle last a bit
                subs.append([event.timeStart + offset, event.timeEnd + offset + defaultDuration, event.styleStart + event.sub + event.styleEnd])
            else:
                subs.append([event.timeStart + offset, event.timeEnd + offset, event.styleStart + event.sub + event.styleEnd])

        # Reorder the events in the subtitles list, according to their starttime
        subs.sort(key=lambda t: (t[0].hour, t[0].minute, t[0].second, t[0].microsecond))

        subtext = ""
        for i, sub in enumerate(subs):
            subtext += str(i + 1) + "\r\n" + str(Event.Event.convertTimeStandard2String(sub[0])) + " --> " + str(Event.Event.convertTimeStandard2String(sub[1])) + "\r\n" + str(sub[2]) + "\r\n\r\n"

        return subtext
