"""
Created on 14 mars 2011

@author: F. Bouchet (francois.bouchet@mcgill.ca)
"""

from Events.Event import MTEvent, MTUnknownEventException
#from MetaTutor.Events.Quiz import MTQuizEvent
#from MetaTutor.Log import Logger

### TYPE 2 EVENTS ###
class MTRuleEvent(MTEvent):
    def __init__(self, logger, eventID, absolutetime, timestamp):
        MTEvent.__init__(self, logger, eventID, 2, absolutetime, timestamp)

    def getInfo(self, showAll=False):
        l = MTEvent.getInfo(self, showAll)
        return l

class MTRuleSRLEvent(MTRuleEvent):  # AdaptiveRules
    """Event happening when the user is performing a SRL process, either on his own initiative, or to answer to a prompt from the agent"""
    def __init__(self, logger, eventID, absolutetime, timestamp, returnCode):
        MTRuleEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        #self.returnCode = eventInfo[0]    # for the version creating SRLEvents only
        self.returnCode = returnCode
        """Code returned by the event"""
        #self.SRLType = eventInfo[2][1:].split(']')[0]
        #if self.SRLType not in ["PLAN","SUMM","TN","MPTG","RR","COIS","PKA","JOL","FOK","CE","INF"]:
        #    self.SRLType = "Unknown"
        #    print eventInfo
        self.SRLType = ""
        """Name of the SRL type"""
        self.sub = "SRL event: <b>" + self.SRLType + "</b>"
        """Subtitle associated with this event"""
        #self.styleStart = "<b>"
        #self.styleEnd = "</b>"
        self.initiative = None
        """The person who initiated the SRL event (agent, user or None in some cases)"""
        self.rule = None
        """The MT kind of rule associated to this SRL event"""
        self.flow = None
        """The flow in which this event is taking place"""
        self.startingAction = None
        """The unique identifier of the action associated with the trigger of this event"""

    def __str__(self):
        return self.SRLType + ":\t " + self.rule + "\t - " + self.flow + "\t - " + self.startingAction

    @staticmethod
    def initRuleAction(eventInfo, SRLType):
        try:    # extract the following pieces of information from the string
            rule = eventInfo[2].split("rule:")[1].split(")")[0]
            for i in range(rule.count("(")):    # if there are parentheses in the rule name, readd missing elements
                rule = rule + ")" + eventInfo[2].split("rule:")[1].split(")")[i+1]
            flow = eventInfo[2].split("Starting action: ")[1].split("(")[0]
            startingAction = eventInfo[2].split("Starting action: ")[1].split("(")[1][:-1]
            return [rule, flow, startingAction]
        except IndexError:
            raise MTUnknownEventException("Unknown rule, flow or starting action value while creating a MTRule" + str(SRLType) + "Event: " + str(eventInfo))

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = MTRuleEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.rule, self.flow, self.startingAction, self.initiative])
        else:
            if showRule:
                l.append(self.rule)
            if showFlow:
                l.append(self.flow)
            if showStartingAction:
                l.append(self.startingAction)
            if showInitiative:
                l.append(self.initiative)
        return l


class MTRulePLANEvent(MTRuleSRLEvent):   # Planification SRL
    """Event happening when the user plans/is advised to plan his upcoming actions (by setting up subgoals, postponing his current subgoal, etc.)"""
    PLANstartingactions = {"start":[" - setting up first subgoals"],
                           "PostTestIntro":[" - waiting for post-test"],
                           "AskIfPostponeSubgoal":[" - postponing current subgoal"],
                           "SuggestAddNewSubgoal":[" - suggested considering new subgoal"],
                           "newSubgoal":[" - setting up new subgoal"]}

    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "PLAN"
        [self.rule, self.flow, self.startingAction] = MTRuleSRLEvent.initRuleAction(eventInfo, self.SRLType)

        if self.startingAction in self.PLANstartingactions.keys():
            self.sub += self.PLANstartingactions[self.startingAction][0]
        else:
            logger.warning("Unknown kind of PLAN found while initializing: " + self.rule)

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            pass
        return l

class MTRuleSUMMEvent(MTRuleSRLEvent):   # Summarization
    """Event happening when the user types/is advised to type a summary of what he has just learnt"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "SUMM"
        [self.rule, self.flow, self.startingAction] = MTRuleSRLEvent.initRuleAction(eventInfo, self.SRLType)
        if self.startingAction == "SumPrompt" or self.startingAction == "SumPromptOnLeave" or self.startingAction == "SumPromptSystem":
            self.initiative = "agent"
            self.sub += " - agent prompt"
        elif self.startingAction == "Sum" or self.startingAction == "SumEarly":
            self.initiative = "user"
            self.sub += " - user initiative"
        else:
            self.initiative = None
            logger.warning("Unknown kind of SUMM found while initializing: " + self.startingAction)

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            pass
        return l

class MTRuleTNEvent(MTRuleSRLEvent):   # Taking Note
    """Event happening when the user takes/is advised to take some notes within the note-taking interface embedded in MetaTutor"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "TN"
        if len(eventInfo[2]) > 4:    # if there is some text following the [TN]
            [self.rule, self.flow, self.startingAction] = MTRuleSRLEvent.initRuleAction(eventInfo, self.SRLType)
        else:
            # a lot of TN don't have any associated values, so no warnings shall be displayed
            # print "Warning: TN without rule, flow and startingAction information"
            [self.rule, self.flow, self.startingAction] = ["","",""]
        if self.startingAction in ["DrawWithImageOpened", "DrawWithImageNotOpened"]:
            self.initiative = "agent"
            self.sub += " - agent prompt"
        else:
            self.initiative = "user"
            self.sub += " - user initiative"

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            pass
        return l

class MTRuleMPTGEvent(MTRuleSRLEvent):   # Managing Progress Towards Goal
    """Event happening when the user manages/is requested to manage his progression towards his current subgoal by assessing his understanding so far"""
    MPTGrules = {"User MPTG appropriate":["user", "appropriate", " - user initiative (appropriate)"],
                 "User MPTG too early":["user", "too early", " - user initiative (too early)"],
                 "Prompt MPTG on time limit":["agent", "time limit", " - agent prompt (time limit)"],
                 "Prompt MPTG on percent complete":["agent", "percent complete", " - agent prompt (percent complete)"]}

    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "MPTG"
        [self.rule, self.flow, self.startingAction] = MTRuleSRLEvent.initRuleAction(eventInfo, self.SRLType)

        if self.rule in self.MPTGrules.keys():
            self.initiative = self.MPTGrules[self.rule][0]
            self.trigger = self.MPTGrules[self.rule][1]
            self.sub += self.MPTGrules[self.rule][2]
        else:
            logger.warning("Unknown kind of MPTG found while initializing: " + self.rule)

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False, showTrigger=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            l.extend([self.trigger])
        else:
            if showTrigger:
                l.append(self.trigger)
        return l

class MTRuleRREvent(MTRuleSRLEvent):   # ReReading
    """Event happening when the user is advised to read again a particular content"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "RR"
        [self.rule, self.flow, self.startingAction] = MTRuleSRLEvent.initRuleAction(eventInfo, self.SRLType)
        self.initiative = "agent"
        self.sub += " - agent prompt"

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            pass
        return l

class MTRuleCOISEvent(MTRuleSRLEvent):   # COordination of Information from different Sources
    """Event happening when the user is advised to coordinate information from different sources (text and image)"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "COIS"
        [self.rule, self.flow, self.startingAction] = MTRuleSRLEvent.initRuleAction(eventInfo, self.SRLType)
        self.initiative = "agent"
        self.sub += " - agent prompt"

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            pass
        return l

class MTRulePKAEvent(MTRuleSRLEvent):   # Prior Knowledge Activation
    """Event happening when the user is activating/requested to activate prior knowledge regarding the subgoal he is pursuing"""
    PKArules = {"Prompt for PKA at the start of a subgoal":["agent", " - first agent prompt"],
                "PKA Prompt":["agent", " - agent prompt"],
                "User PKA":["user", " - user initiative"]}

    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "PKA"
        [self.rule, self.flow, self.startingAction] = MTRuleSRLEvent.initRuleAction(eventInfo, self.SRLType)

        if self.rule in self.PKArules.keys():
            self.initiative = self.PKArules[self.rule][0]
            self.sub += self.PKArules[self.rule][1]
        else:
            logger.warning("Unknown kind of PKA found while initializing: " + self.rule)

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            pass
        return l

class MTRuleJOLEvent(MTRuleSRLEvent):   # Judgment of Learning
    """Event happening when the user is judging/requested to judge how well he has just learnt about the content he had been reading"""
    JOLrules = {"User JOL":["user", None, " - user initiative"],
                "Prompt JOL":["agent", "appropriate", " - agent prompt"],
                "Prompt JOL when page is changing sooner than enough":["agent", "too quick", " - agent prompt (probably too quick)"]}

    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "JOL"
        [self.rule, self.flow, self.startingAction] = MTRuleSRLEvent.initRuleAction(eventInfo, self.SRLType)

        if self.rule in self.JOLrules.keys():
            self.initiative = self.JOLrules[self.rule][0]
            """Person responsible for the trigger of this event (agent or user)"""
            self.trigger = self.JOLrules[self.rule][1]
            """Was the event triggered at an appropriate time or too early ?"""
            self.sub += self.JOLrules[self.rule][2]
            """Subtitle associated to the event"""
        else:
            logger.warning("Unknown kind of JOL found while initializing: " + self.rule)

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False, showTrigger=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            l.extend([self.trigger])
        else:
            if showTrigger:
                l.append(self.trigger)
        return l

class MTRuleFOKEvent(MTRuleSRLEvent):   #  Feeling of Knowing
    """Event happening when the user is expressing/requested to express his feeling to know/not to know about the content of a page"""
    FOKrules = {"User FOK":["user", " - user initiative"],
                "Prompt FOK":["agent", " - agent prompt"],
                "":[None, ""]}      # the FOK corresponds to the answer to a DEPENDS - nothing to add in that case

    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "FOK"
        if len(eventInfo[2]) > 5:    # if there is some text following the [FOK]
            [self.rule, self.flow, self.startingAction] = MTRuleSRLEvent.initRuleAction(eventInfo, self.SRLType)
        else:
            # is in answer to a "why did you leave this page so early?"
            #logger.warning("FOK without rule, flow and startingAction information")
            [self.rule, self.flow, self.startingAction] = ["","",""]

        if self.rule in self.FOKrules.keys():
            self.initiative = self.FOKrules[self.rule][0]
            self.sub += self.FOKrules[self.rule][1]
        else:
            logger.warning("Unknown kind of FOK found while initializing: " + self.rule)

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            pass
        return l

class MTRuleCEEvent(MTRuleSRLEvent):   #  Content Evaluation
    """Event happening when the user evaluates/is requested to evaluate the relevance of a given page to help him moving toward his current subgoal"""
    CEstartingActions = {"CERelevant":["user", True, " - user initiative (relevant page)"],
                         "CEIrrelevant":["user", False, " - user initiative (irrelevant page)"],
                         "CERelevantPrompt":["agent", True, " - agent prompt (relevant page)"],
                         "CEIrrelevantPrompt":["agent", False, " - agent prompt (irrelevant page)"],
                         "CEPageIrrelevantImgIrrelevantNotOpened":["agent", False, " - agent prompt (irrelevant page)"],
                         "CEPageIrrelevantImgIrrelevantOpened":["agent", False, " - agent prompt (irrelevant page)"],
                         "CEPageRelevantImgRelevantOpened":["agent", True, " - agent prompt (relevant page)"],
                         "CEPageRelevantImgRelevantNotOpened":["agent", True, " - agent prompt (relevant page)"],
                         "CERelevantPrompt":["agent", True, " - agent prompt (relevant page)"],
                         "CEPageIrrelevantImgRelevantOpened":["agent", False, " - agent prompt (irrelevant page)"],
                         "CEPageIrrelevantImgRelevantNotOpened":["agent", False, " - agent prompt (irrelevant page)"],
                         "CEPageRelevantImgIrrelevantOpened":["agent", False, " - agent prompt (irrelevant page)"],
                         "CEPageRelevantImgIrrelevantNotOpened":["agent", False, " - agent prompt (irrelevant page)"],
                         "":["agent", None, " - agent prompt for a page left too quickly"]}


    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "CE"
        if len(eventInfo[2]) > 4:    # if there is some text following the [CE]
            [self.rule, self.flow, self.startingAction] = MTRuleSRLEvent.initRuleAction(eventInfo, self.SRLType)
        else:
            # is in answer to a "why did you leave this page so early?"
            #logger.warning("CE without rule, flow and startingAction information")
            [self.rule, self.flow, self.startingAction] = ["","",""]

        if self.startingAction in self.CEstartingActions.keys():
            self.initiative = self.CEstartingActions[self.startingAction][0]
            self.realRelevancy = self.CEstartingActions[self.startingAction][1]
            self.sub += self.CEstartingActions[self.startingAction][2]
        else:
            logger.warning("Unknown kind of CE found while initializing: " + self.rule)

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False, showRealRelevancy=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            l.extend([self.realRelevancy])
        else:
            if showRealRelevancy:
                l.append(self.realRelevancy)
        return l

class MTRuleINFEvent(MTRuleSRLEvent):   #  Inference
    """Event happening when the user makes an inference about the content of a page"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "INF"
        [self.rule, self.flow, self.startingAction] = MTRuleSRLEvent.initRuleAction(eventInfo, self.SRLType)
        self.initiative = "user"
        self.sub += " - user initiative"

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            pass
        return l

class MTRuleDependsEvent(MTRuleSRLEvent):   # Depends
    """Event happening when the user leaves a page too quickly and that the agent asks him to justify his behavior by picking a relevant SRL process (CE or FOK)"""
    dictDependsSRL = {"PageIrrelevant":["CE", " CE (ContentEvaluation)"],
                      "KnowContent":["FOK (before page read)", " FOK (FeelingOfKnowing before page read)"],
                      "PageRead":["FOK (after page read)", " FOK (FeelingOfKnowing after page read)"],
                      "Cancel":["no SRL", " no SRL (user cancels)"]}

    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "DEPENDS"
        #: the real SRL type can only be defined during the extended log analysis and takes value in ["CE", "FOK (before page read)", "FOK (after page read)", "no SRL"]
        self.realSRLType = None
        [self.rule, self.flow, self.startingAction] = MTRuleSRLEvent.initRuleAction(eventInfo, self.SRLType)
        self.sub += " - page left too quickly"

    def setRealSRLType(self, logger, key):
        try:
            self.realSRLType = self.dictDependsSRL[key][0]
            self.sub += self.dictDependsSRL[key][1]
        except KeyError:
            logger.warning("Unknown kind of input value for a DEPENDS: " + key)

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False, showRealSRLType=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            l.extend([self.realSRLType])
        if showRealSRLType:
            l.append(self.realSRLType)
        return l

class MTRuleSRLUnknownEvent(MTRuleSRLEvent):    # for all the other events from the log
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleSRLEvent.__init__(self, logger, eventID, absolutetime, timestamp, eventInfo[0])
        self.SRLType = "Unknown"
        # Handle the "known" unknowns, i.e. those which cause has been identified
        # not to mix them with real unknown events
        if eventInfo[2] == " No appropiate user rule found for user action CE":     # typo needed: it's like that in the log
            logger.warning("Problematic event with known origin: User doing a CE while no SG is set")
        elif eventInfo[2] == "(rule:PKA Prompt) value 65 for parameter PreTestPerformanceOnCurrentSubgoal is not an integer value.":     
            logger.warning("Problematic event with known origin: Buggued PKA value")
        else:
            logger.warning("UNKNOWN event: " + str(eventInfo))
        [self.rule, self.flow, self.startingAction] = ["","",""]

    def getInfo(self, showAll=False, showRule=False, showFlow=False, showStartingAction=False, showInitiative=False):
        l = MTRuleSRLEvent.getInfo(self, showAll, showRule, showFlow, showStartingAction, showInitiative)
        if showAll:
            pass
        return l

class MTRuleMeasureEvent(MTRuleEvent):
    """Event happening when a user starts taking a questionnaire (in MT 1.2.x and above)"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        self.styleStart = '<font color="#339900">'
        self.styleEnd = '</font>'
        self.questionnaireName = eventInfo[2].split('(')[-1].split(')')[0]

    def getInfo(self, showAll=False, showQuestionnaireName=False):
        l = MTRuleEvent.getInfo(self, showAll)
        if showAll or showQuestionnaireName:
            l.append(self.questionnaireName)
        return l

class MTRuleQuizEvent(MTRuleEvent): # MonitoringFlow        # not directly used for subtitles
    """Event happening when a user starts taking a quiz"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        self.styleStart = '<font color="#339900">'
        self.styleEnd = '</font>'
        self.about = eventInfo[2].split("Begin quiz for ")[1].split()[0]
        self.contentIdx = eventInfo[2].split()[-1]
        """Type of content to which the quiz is related (can be a page or a subgoal)"""

    def getInfo(self, showAll=False, showAbout=False, showContentIdx=False):
        l = MTRuleEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.about, self.contentIdx])
        if showContentIdx:
            l.append(self.contentIdx)
        if showAbout:
            l.append(self.about)
        return l

class MTRuleFlowCantStart(MTRuleEvent):
    """Event happening when a SRL event has been triggered while one was already in progress (and should therefore be ignored)"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        tmptxt = eventInfo[2].split("because")[0]
        self.eventToCancel = ""
        for srl in ["PLAN", "SUMM", "TN", "MPTG", "RR", "COIS", "PKA", "JOL", "FOK", "CE", "INF", "MeasureFlow"]:
            if srl in tmptxt:
                self.eventToCancel = srl
                break
        if self.eventToCancel == "":
            logger.error("Unknown event to be canceled: " + str(eventInfo))

# TODO:
class MTRuleDigimemoEvent(MTRuleEvent): # not implemented as they aren't really useful (only to know the link is done)
    """Technical event happening to let the system know the note-taking Digimemo device is properly connected"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTRuleEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        self.info = eventInfo[0]
