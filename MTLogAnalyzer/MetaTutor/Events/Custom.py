'''
Created on 22 mars 2011

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

import datetime
from MetaTutor.Events.Event import Event

class CEvent(Event):
    """A customized event, having necessarily a start time and an end time"""
    def __init__(self, logger, ts, te, style=""):
        Event.__init__(self, logger, style)
        self.timeStart = ts
        """Datetime object corresponding to when the event is starting in MT time referential"""
        self.timeEnd = te
        """Datetime object corresponding to when the event is ending in MT time referential"""
        self.duration = self.timeEnd - self.timeStart
        """Datetime object representing the duration of an event"""
        self.punctual = (self.timeEnd == self.timeStart)
        """Boolean indicating if an element is punctual (i.e. if its duration is of 0s)"""
        self.sub = ""
        """Subtitle associated with this event"""
    
    def changeTimeReferential(self, offset):
        """Add an offset to get into a particular video format for the timestamps"""
        offsetTime = datetime.timedelta(seconds=offset)
        self.timeStart += offsetTime
        if self.timeEnd != None:
            self.timeEnd += offsetTime
            
    def getInfo(self, showAll=False):
        l = Event.getInfo(self, showAll)
        l.extend([Event.convertTimeStandard2String(self.timeStart), Event.convertTimeStandard2String(self.timeEnd), Event.convertTimeDelta2String(self.duration)])
        return l
        
    def getTimeStart(self):
        return self.timeStart
    def getTimeEnd(self):
        return self.timeEnd

class CEvtNoteTakeGUI(CEvent):
    """Event starting when the participant starts taking notes in the online graphical user interface,
    and ending when he closes the Notes interface"""
    def __init__(self, logger, timeStart, timeEnd, interrupted=False, pageId=None, MTevt=None):
        CEvent.__init__(self, logger, timeStart, timeEnd, "Notes")
        self.interrupted = interrupted
        """Boolean indicating if the participant has been interrupted by an agent prompt that closed the note-taking GUI"""
        self.pageID = pageId
        """ID of the page the participant was viewing when opening the note-taking GUI"""
        if self.interrupted:
            self.sub = "User taking/checking notes but interrupted"
            """Subtitle associated with this event"""
        else:
            self.sub = "User taking notes while on page " + self.pageID
        self.MTEvent = MTevt
        """ID of the associated SUMM event in MT log"""
    
    def getInfo(self, showAll=False, showPageId=False, showIfInterrupted=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.pageID, self.interrupted])
        else:
            if showPageId:
                l.append(self.pageID)
            if showIfInterrupted:
                l.append(self.interrupted)
        return l

class CEvtNoteCheckGUI(CEvent):
    """Event starting when the participant opens the Notes interface,
    and ending when he closes it without having taken any notes"""
    def __init__(self, logger, timeStart, timeEnd, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd, "Notes")
        self.sub = "User checking notes"
        """Subtitle associated with this event"""
        self.MTEvent = MTevt
        """ID of the associated SUMM event in MT log"""
        
    def getInfo(self, showAll=False):
        return CEvent.getInfo(self, showAll)
    
class CEvtNoteAddedFromSummary(CEvent):
    """Punctual event happening when the participant is accepting agent's offer to add a summary to his/her notes"""
    def __init__(self, logger, timeStart):
        CEvent.__init__(self, logger, timeStart, timeStart, "UserActivity")
        self.sub = "User adding summary to notes"
        """Subtitle associated with this event"""
        
    def getInfo(self, showAll=False):
        return CEvent.getInfo(self, showAll)
    
class CEvtNoteNotAddedFromSummary(CEvent):
    """Punctual event happening when the participant is refusing agent's offer to add a summary to his/her notes"""
    def __init__(self, logger, timeStart):
        CEvent.__init__(self, logger, timeStart, timeStart, "UserActivity")
        self.sub = "User refusing to add summary to notes"
        """Subtitle associated with this event"""
    
    def getInfo(self, showAll=False):
        return CEvent.getInfo(self, showAll)
        
class CEvtNoteTakenOnPaper(CEvent):
    """Event starting when the participant's pen enters in contact with the sheet of paper of the Digimemo
     and ending when the pen is lifted"""
    def __init__(self, logger, timeStart, timeEnd):
        CEvent.__init__(self, logger, timeStart, timeEnd, "Notes")
        self.sub = "User taking notes on Digimemo"
        """Subtitle associated with this event"""
        
    def getInfo(self, showAll=False):
        return CEvent.getInfo(self, showAll)
    
class CEvtVideoIsPlaying(CEvent):
    """Event starting when a video is being shown to the participant,
    and ending when the video ends"""
    def __init__(self, logger, timeStart, timeEnd, videoName):
        CEvent.__init__(self, logger, timeStart, timeEnd, "Browse")
        self.videoName = videoName
        """Name of the video that is being played"""
        self.sub = "Video " + self.videoName + " playing"
        """Subtitle associated with this event"""
        
    def getInfo(self, showAll=False, showVideoName=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.videoName])
        else:
            if showVideoName:
                l.append(self.videoName)
        return l

class CEvtQuestionnaireOngoing(CEvent):
    """Event starting when a questionnaire is being administered to the participant,
    and ending when the replies are submitted"""
    def __init__(self, logger, timeStart, timeEnd, questionnaireName):
        CEvent.__init__(self, logger, timeStart, timeEnd, "Browse")
        self.questionnaireName = questionnaireName
        """Name of the questionnaire that is being administered"""
        self.sub = "Questionnaire " + self.questionnaireName + " ongoing"
        """Subtitle associated with this event"""
        
    def getInfo(self, showAll=False, showQuestionnaireName=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.questionnaireName])
        else:
            if showQuestionnaireName:
                l.append(self.questionnaireName)
        return l
        
class CEvtAgentSpeaking(CEvent):
    """Event starting when an agent starts speaking,
    and ending when the vocalization is over"""
    def __init__(self, logger, timeStart, timeEnd, timeStartAbsolute, timeEndAbsolute, agentName):
        CEvent.__init__(self, logger, timeStart, timeEnd)
        # TMP FIX FOR AIED
        self.timeStartAbsolute = timeStartAbsolute
        self.timeEndAbsolute = timeEndAbsolute
        self.agentName = agentName
        """Name of the agent who is currently speaking (Gavin | Pam | Mary | Sam)"""
        self.sub = self.agentName + " speaking"
        """Subtitle associated with this event"""
        
    def getInfo(self, showAll=False, showAgentSpeaking=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.convertTimeStandard2String(self.timeStartAbsolute), self.convertTimeStandard2String(self.timeEndAbsolute), self.agentName])
        else:
            if showAgentSpeaking:
                l.append(self.agentName)
        return l
        
class CEvtAgentRemindsTimeLeft(CEvtAgentSpeaking):
    """Event starting when an agent starts speaking to remind the time left,
    and ending when the vocalization is over"""
    def __init__(self, logger, timeStart, timeEnd, timeStartAbsolute, timeEndAbsolute, agentName, timeLeft):
        CEvtAgentSpeaking.__init__(self, logger, timeStart, timeEnd, timeStartAbsolute, timeEndAbsolute, agentName)
        self.timeLeft = timeLeft
        """Remaining time before the end of the session"""
    
    def getInfo(self, showAll=False, showTimeLeft=False, showAgentSpeaking=False):
        l = CEvtAgentSpeaking.getInfo(self, showAll, showAgentSpeaking)
        if showAll:
            l.extend([self.timeLeft])
        else:
            if showTimeLeft:
                l.append(self.timeLeft)
        return l

class CEvtUserTypingSummary(CEvent):
    """Event starting when the user starts typing a summary,
    and ending when he submits it to the agent"""
    def __init__(self, logger, timeStart, timeEnd, initiative, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd, "UserActivity")
        self.sub = "User typing SUMM "
        """Subtitle associated with this event"""
        if initiative in ["user", "agent"]:
            self.initiative = initiative
            """Person who decided to type a summary in the first place (user or agent)"""
            self.sub += ("on his own decision" if self.initiative == "user" else "after agent's prompt")
        else:
            self.initiative = None
            logger.warning("Unknown value for initiative: " + initiative)
        self.MTEvent = MTevt
        """ID of the associated SUMM event in MT log"""
            
    def getInfo(self, showAll=False, showInitiative=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.initiative])
        else:
            if showInitiative:
                l.append(self.initiative)
        return l

class CEvtUserTypingPKA(CEvent):
    """Event starting when the user starts typing a prior knowledge activation text,
    and ending when he submits it to the agent"""
    def __init__(self, logger, timeStart, timeEnd, initiative, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd, "UserActivity")
        self.sub = "User typing PKA "
        """Subtitle associated with this event"""
        if initiative in ["user", "agent"]:
            self.initiative = initiative
            """Person who decided to type a PKA in the first place (user or agent)"""
            self.sub += ("on his own decision" if self.initiative == "user" else "after agent's prompt")
        else:
            self.initiative = None
            logger.warning("Unknown value for initiative: " + initiative)
        self.MTEvent = MTevt
        """ID of the associated PKA event in MT log"""

    def getInfo(self, showAll=False, showInitiative=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.initiative])
        else:
            if showInitiative:
                l.append(self.initiative)
        return l

class CEvtUserTypingINF(CEvent):
    """Event starting when the user starts typing an inference,
    and ending when he submits it to the agent"""
    def __init__(self, logger, timeStart, timeEnd, initiative, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd, "UserActivity")
        self.sub = "User typing INF"
        """Subtitle associated with this event"""
        if initiative in ["user", "agent"]:
            self.initiative = initiative
            """Who took the initiative of this SRL event? Can be 'user', 'agent' or None."""
            self.sub += ("on his own decision" if self.initiative == "user" else "after agent's prompt")
        else:
            self.initiative = None
            logger.warning("Unknown value for initiative: " + initiative)
        self.MTEvent = MTevt
        """ID of the associated INF event in MT log"""
    
    def getInfo(self, showAll=False, showInitiative=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.initiative])
        else:
            if showInitiative:
                l.append(self.initiative)
        return l
            
class CEvtUserEvaluatingContentCE(CEvent):
    """Event starting when the user starts a CE,
    and ending when he picks which element he finds relevant to his subgoal"""
    CEeval = {"None":" - answer = none",
              "Image":" - answer = image only",
              "Page":" - answer = page only",
              "Both":" - answer = page + image"}
    
    def __init__(self, logger, timeStart, timeEnd, relevance, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd)
        if relevance in self.CEeval.keys():
            self.evaluatedRelevance = relevance
            """Element considered as relevant by the user (taking value in [None, Image, Page, Both])"""
            self.sub = MTevt.sub + self.CEeval[relevance]
            """Subtitle associated with this event"""
        else:
            self.evaluatedRelevance = None
            logger.warning("Unknown value for relevant element: " + relevance)
        # to retrieve parameters from the corresponding MTRuleCEEvent
        self.MTEvent = MTevt
        """ID of the associated CE event in MT log"""
        
    def getInfo(self, showAll=False, showEvaluatedRelevance=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False, showRealRelevancy=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.evaluatedRelevance])
        else:
            if showEvaluatedRelevance:
                l.append(self.evaluatedRelevance)
        # call the function from the associated CE event, dropping the 3 first fields (timestart, timeend, event name) which aren't needed here
        l.extend(self.MTEvent.getInfo(showAll, showRule, showFlow, showStartingAction, showInitiative, showRealRelevancy)[3:])
        return l

class CEvtUserMovingTowardGoalMPTG(CEvent):
    """Event starting when the user starts a MPTG,
    and ending when he confirms it"""
    def __init__(self, logger, timeStart, timeEnd, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd)
        # to retrieve parameters from the corresponding MTRuleMPTGEvent
        self.MTEvent = MTevt
        """The associated MPTG event in MT log"""
        self.sub = MTevt.sub + " - and finally moves towards goal"
        """Subtitle associated with this event"""
    
    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False, showTrigger=False):
        l = CEvent.getInfo(self, showAll)
        # call the function from the associated MPTG event
        l.extend(self.MTEvent.getInfo(showAll, showRule, showFlow, showStartingAction, showInitiative, showTrigger)[3:])
        return l
        
class CEvtUserNotMovingTowardGoalMPTG(CEvent):
    """Event starting when the user starts a MPTG,
    and ending when he finally cancels it"""
    def __init__(self, logger, timeStart, timeEnd, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd)
        # to retrieve parameters from the corresponding MTRuleMPTGEvent
        self.MTEvent = MTevt
        """The associated MPTG event in MT log"""
        self.sub = MTevt.sub + " - and finally refuses to move towards goal"
        """Subtitle associated with this event"""
    
    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False, showTrigger=False):
        l = CEvent.getInfo(self, showAll)
        # call the function from the associated MPTG event
        l.extend(self.MTEvent.getInfo(showAll, showRule, showFlow, showStartingAction, showInitiative, showTrigger)[3:])
        return l
        
class CEvtUserJudgingLearningJOL(CEvent):
    """Event starting when the user starts a JOL,
    and ending when he rates his understanding on a 1 to 6 scale"""
    JOLeval = {"1":" - strongly doesn't understand",
               "2":" - doesn't understand",
               "3":" - somewhat doesn't understand",
               "4":" - somewhat understands",
               "5":" - understands",
               "6":" - strongly understands"}
    
    def __init__(self, logger, timeStart, timeEnd, understanding, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd)
        try:
            if int(understanding) in range(1,7):
                self.understandingLevel = (understanding if int(understanding) in range(1,7) else None)
                """Level of understanding assessed by the participant (from 1 for strong lack of understanding to 6 for strong understanding)"""
                self.sub = MTevt.sub + self.JOLeval[understanding]
                """Subtitle associated with this event"""
        except ValueError:  # not a number
            self.understandingLevel = None
        if self.understandingLevel == None:
            logger.warning("Unknown value for understanding level: " + understanding)
        # to retrieve parameters from the corresponding MTRuleJOLEvent
        self.MTEvent = MTevt
        """The associated JOL event in MT log"""
        
    def getInfo(self, showAll=False, showUnderstandingLevel=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False, showTrigger=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.understandingLevel])
        else:
            if showUnderstandingLevel:
                l.append(self.understandingLevel)
        # call the function from the associated JOL event, dropping the 3 first fields (timestart, timeend, event name) which aren't needed here
        l.extend(self.MTEvent.getInfo(showAll, showRule, showFlow, showStartingAction, showInitiative, showTrigger)[3:])
        return l

class CEvtUserFeelingKnowledgeFOK(CEvent):
    """Event starting when the user starts a FOK,
    and ending when he rates his knowledge on a 1 to 6 scale"""
    FOKeval = {"1":" - strongly doesn't know",
               "2":" - doesn't know",
               "3":" - somewhat doesn't know",
               "4":" - somewhat knows",
               "5":" - knows",
               "6":" - strongly knows"}
    
    def __init__(self, logger, timeStart, timeEnd, knowledge, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd)
        try:
            if int(knowledge) in range(1,7):
                self.knowledgeLevel = (knowledge if int(knowledge) in range(1,7) else None)
                """Knowledge level assessed by the participant (from 1 for strong lack of knowledge to 6 for strong knowledge)"""
                self.sub = MTevt.sub + self.FOKeval[knowledge]
                """Subtitle associated with this event"""
        except ValueError:  # not a number
            self.knowledgeLevel = None
        if self.knowledgeLevel == None:
            logger.warning("Unknown value for knowledge level: " + knowledge)
        # to retrieve parameters from the corresponding MTRuleFOKEvent
        self.MTEvent = MTevt
        """ID of the associated FOK event in MT log"""

    def getInfo(self, showAll=False, showKnowledgeLevel=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.knowledgeLevel])
        else:
            if showKnowledgeLevel:
                l.append(self.knowledgeLevel)
        # call the function from the associated FOK event, dropping the 3 first fields (timestart, timeend, event name) which aren't needed here
        l.extend(self.MTEvent.getInfo(showAll, showRule, showFlow, showStartingAction, showInitiative)[3:])
        return l
            
class CEvtInitialSubgoalsSetting(CEvent):
    """Event starting when the user starts setting up its first 3 subgoals,
    and ending when they have been correctly set up"""
    def __init__(self, logger, timeStart, timeEnd, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd)
        self.MTEvent = MTevt
        """The associated SG event in MT log"""
        self.sub = "SRL event: <b>PLAN</b> - setting up first subgoals"
        """Subtitle associated with this event"""
        
    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = CEvent.getInfo(self, showAll)
        # call the function from the associated PLAN event
#        l.extend(self.MTEvent.getInfo(showAll, showRule, showFlow, showStartingAction, showInitiative)[3:])
        return l

class CEvtSubgoalSetting(CEvent):
    """Event starting when the user starts setting up a subgoal,
    and ending when it has been correctly set up"""
    def __init__(self, logger, timeStart, timeEnd, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd)
        self.MTEvent = MTevt
        """The associated SG event in MT log"""
        self.sub = "SRL event: <b>PLAN</b> - setting up new subgoal"
        """Subtitle associated with this event"""
        
    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = CEvent.getInfo(self, showAll)
        # call the function from the associated PLAN event
#        l.extend(self.MTEvent.getInfo(showAll, showRule, showFlow, showStartingAction, showInitiative)[3:])
        return l

class CEvtSubgoalSuggested(CEvent):
    """Punctual event happening when the agent suggests to the user to set up a new subgoal"""
    def __init__(self, logger, timeStart):
        CEvent.__init__(self, logger, timeStart, timeStart)
        self.sub = "SRL event: <b>PLAN</b> - suggested considering new subgoal"
        """Subtitle associated with this event"""
        
    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = CEvent.getInfo(self, showAll)
        # call the function from the associated PLAN event
#        l.extend(self.MTEvent.getInfo(showAll, showRule, showFlow, showStartingAction, showInitiative)[3:])
        return l
        
class CEvtPostponingSubgoal(CEvent):
    """Event starting when the user asks to change his current subgoal,
    and ending when it accepts to do so after agent's asked for confirmation"""
    def __init__(self, logger, timeStart, timeEnd, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd)
        self.MTEvent = MTevt
        """The associated SG event in MT log"""
        self.sub = "SRL event: <b>PLAN</b> - postponing current subgoal"
        """Subtitle associated with this event"""
        
    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = CEvent.getInfo(self, showAll)
        # call the function from the associated PLAN event
#        l.extend(self.MTEvent.getInfo(showAll, showRule, showFlow, showStartingAction, showInitiative)[3:])
        return l
        
class CEvtNotPostponingSubgoal(CEvent):
    """Event starting when the user asks to change his current subgoal,
    and ending when it refuses to do so after agent's asked for confirmation"""
    def __init__(self, logger, timeStart, timeEnd, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd)
        self.MTEventID = MTevt
        """The associated SG event in MT log"""
        self.sub = "SRL event: <b>PLAN</b> - postponing current subgoal (user cancels)"
        """Subtitle associated with this event"""
    
    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = CEvent.getInfo(self, showAll)
        # call the function from the associated PLAN event
#        l.extend(self.MTEvent.getInfo(showAll, showRule, showFlow, showStartingAction, showInitiative)[3:])
        return l

class CEvtSubgoalSet(CEvent):
    """Punctual event happening when the user has picked a subgoal, following a request from the agent to 
    either choose in a list of 2 to 3 subgoals, or confirm a previously requested subgoal"""    
    def __init__(self, logger, timeStart, subgoalNb, subgoalName, subgoalID):
        CEvent.__init__(self, logger, timeStart, timeStart)
        self.subgoalNb = subgoalNb
        """Number in which the subgoal has been set up - shouldn't be above 7, since one can pursue only once every subgoal"""
        if self.subgoalNb < 1 or self.subgoalNb > 7:
            logger.warning("Unknown value for a subgoal: " + str(subgoalNb))
        self.subgoalName = subgoalName
        """Name of one of the 7 possible subgoals"""
        self.subgoalID = subgoalID
        """Code from 1 to 7 corresponding to one of the seven existing subgoals"""
        
    def getInfo(self, showAll=False, showSubgoalNb=False, showSubgoalID=False, showSubgoalName=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.subgoalNb, self.subgoalID, self.subgoalName])
        else:
            if showSubgoalNb:
                l.append(self.subgoalNb)
            if showSubgoalID:
                l.append(self.subgoalID)
            if showSubgoalName:
                l.append(self.subgoalName)
        return l
        
class CEvtPursuingNewSubgoal(CEvent):
    """Punctual event happening when the user starts pursuing a new subgoal"""
    def __init__(self, logger, timeStart, currentSubgoalID):
        CEvent.__init__(self, logger, timeStart, timeStart)
        self.currentSubgoalID = currentSubgoalID
        """Code from 0 to 7 corresponding to the subgoal ID that is currently trying to be learnt 
        (0 for no subgoal, when the user has finished the 3 first ones and not yet set up a new one)"""
    
    def getInfo(self, showAll=False, showCurrentSubgoalID=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.currentSubgoalID])
        else:
            if showCurrentSubgoalID:
                l.append(self.currentSubgoalID)
        return l

class CEvtPursuingSameSubgoal(CEvent):
    """Punctual event happening when the user keeps pursuing the same subgoal after a failed quiz"""
    def __init__(self, logger, timeStart, currentSubgoalID):
        CEvent.__init__(self, logger, timeStart, timeStart)
        self.currentSubgoalID = currentSubgoalID
        """Code from 0 to 7 corresponding to the subgoal ID that is currently trying to be learnt 
        (0 for no subgoal, when the user has finished the 3 first ones and not yet set up a new one)"""
    
    def getInfo(self, showAll=False, showCurrentSubgoalID=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.currentSubgoalID])
        else:
            if showCurrentSubgoalID:
                l.append(self.currentSubgoalID)
        return l
    
class CEvtValidatedSubgoal(CEvent):
    """Punctual event happening when the user has validated a subgoal quiz (regardless of if they want to spend more time on it after)"""
    def __init__(self, logger, timeStart, validatedSubgoalID):
        CEvent.__init__(self, logger, timeStart, timeStart)
        self.validatedSubgoalID = validatedSubgoalID
        """Code from 1 to 7 corresponding to the subgoal ID that has been validated (can't be 0 since no quizzes are possible when no subgoals are set)"""
        
    def getInfo(self, showAll=False, showValidatedSubgoalID=False):
        l = CEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.validatedSubgoalID])
        else:
            if showValidatedSubgoalID:
                l.append(self.validatedSubgoalID)
        return l
        
class CEvtUserWaitingForPostTest(CEvent):
    """Event starting when the user requests to start the post test,
    and ending when the experimenter has typed the code to allow him to take it"""
    def __init__(self, logger, timeStart, timeEnd, MTevt):
        CEvent.__init__(self, logger, timeStart, timeEnd)
        self.MTEvent = MTevt
        """The associated test event in MT log"""
        self.sub = "SRL event: <b>PLAN</b> - waiting for post-test"
        """Subtitle associated with this event"""
        
    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = CEvent.getInfo(self, showAll)
        # call the function from the associated PLAN event
        l.extend(self.MTEvent.getInfo(showAll, showRule, showFlow, showStartingAction, showInitiative)[3:])
        return l
        
class CEvtUserTakingTest(CEvent):
    """Event starting when the user starts taking a test,
    and ending when the test is over"""
    def __init__(self, logger, timeStart, timeEnd, MTevt, quizEvents):
        CEvent.__init__(self, logger, timeStart, timeEnd, "Quiz")
        self.MTEvent = MTevt
        """ID of the associated test event in MT log"""
        self.sub = "User taking posttest"
        """Subtitle associated with this event"""
        self.quizEvents = quizEvents
        """MTQuizEvent elements associated to this quiz"""
        self.scoreMax = len(self.quizEvents)
        """Maximum score the participant could get on this quiz"""
        self.score = 0
        """Score (i.e. number of correct answers) the participant actually got on this quiz"""
        for qe in self.quizEvents:  # calculates the score
            if qe.answerCorrect:
                self.score += 1
                
    def getInfo(self, showAll=False, showScore=False, showScoreMax=False):
        l = CEvent.getInfo(self, showAll)
        # call the function from the associated MTDialogUserEvent event
        l.extend(self.MTEvent.getInfo(showAll)[:3])
        if showScore or showAll:
            l.append(self.score)
        if showScoreMax or showAll:
            l.append(self.scoreMax)
        return l

class CEvtUserTakingSRLTest(CEvtUserTakingTest):
    """Event starting when the user starts taking the post test,
    and ending when the post test is over"""
    def __init__(self, logger, timeStart, timeEnd, MTevt, quizEvents):
        CEvtUserTakingTest.__init__(self, logger, timeStart, timeEnd, MTevt, quizEvents)
        
    def getInfo(self, showAll=False, showScore=False, showScoreMax=False):
        return CEvtUserTakingTest.getInfo(self, showAll, showScore, showScoreMax)

class CEvtUserTakingPreTest(CEvtUserTakingTest):
    """Event starting when the user starts taking the post test,
    and ending when the post test is over"""
    def __init__(self, logger, timeStart, timeEnd, MTevt, quizEvents):
        CEvtUserTakingTest.__init__(self, logger, timeStart, timeEnd, MTevt, quizEvents)
        
    def getInfo(self, showAll=False, showScore=False, showScoreMax=False):
        return CEvtUserTakingTest.getInfo(self, showAll, showScore, showScoreMax)
    
class CEvtUserTakingPostTest(CEvtUserTakingTest):
    """Event starting when the user starts taking the post test,
    and ending when the post test is over"""
    def __init__(self, logger, timeStart, timeEnd, MTevt, quizEvents):
        CEvtUserTakingTest.__init__(self, logger, timeStart, timeEnd, MTevt, quizEvents)
        
    def getInfo(self, showAll=False, showScore=False, showScoreMax=False):
        return CEvtUserTakingTest.getInfo(self, showAll, showScore, showScoreMax)

class CEvtUserTakingQuiz(CEvent):
    """Event starting when the user starts taking a quiz,
    and ending when the quiz is over"""
    scoreWeightsForQuizAnswers = {"Target":1, "NearMiss":0.5, "Thematic":0.25, "Unrelated":0}
    """weights used to calculated weighted scores to quizzes"""
    
    def __init__(self, logger, timeStart, timeEnd, page, subgoal, quizEvents):
        CEvent.__init__(self, logger, timeStart, timeEnd, "Quiz")
        self.page = page
        """Number of the page associated to this quiz (if it's about a page), starting with 0"""
        self.subgoal = subgoal
        """Number of the subgoal associated to this quiz (if it's about a subgoal), starting with 1"""
        if self.page != None:
            self.sub = "User taking quiz for page " + self.page
            """Subtitle associated with this event"""
        elif self.subgoal != None:
            self.sub = "User taking quiz for subgoal " + self.subgoal
        self.quizEvents = quizEvents
        """MTQuizEvent elements associated to this quiz"""
        self.scoreMax = len(self.quizEvents)
        """Maximum score the participant could get on this quiz"""
        self.score = 0
        """Score (i.e. number of correct answers) the participant actually got on this quiz"""
        self.weightedScore = 0
        """Weighted score of the participant, using the class dictionary for weights"""
        for qe in self.quizEvents:  # calculates the score
            if qe.answerCorrect:
                self.score += 1
            self.weightedScore += CEvtUserTakingQuiz.scoreWeightsForQuizAnswers[qe.answerType]
        
    def getInfo(self, showAll=False, showAssociatedElement=False, showScore=False, showScoreMax=False):
        l = CEvent.getInfo(self, showAll)
        if showAssociatedElement or showAll:
            if self.page != None:
                l.append("Page " + self.page)
            elif self.subgoal != None:
                l.append("Subgoal " + self.subgoal)
            else:
                l.append("Unknown")
        if showScore or showAll:
            l.append(self.score)
        if showScoreMax or showAll:
            l.append(self.scoreMax)
        return l