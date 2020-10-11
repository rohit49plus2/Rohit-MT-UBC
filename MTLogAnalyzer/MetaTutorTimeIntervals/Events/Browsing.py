'''
Created on 17 mars 2011

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

from Events.Event import MTEvent, Event
import datetime

### TYPE 1 EVENTS ###
class MTBrowsingEvent(MTEvent):
    def __init__(self, logger, eventID, absolutetime, timestamp):
        MTEvent.__init__(self, logger, eventID, 1, absolutetime, timestamp, "Browse")

    def getInfo(self, showAll=False):
        l = MTEvent.getInfo(self, showAll)
        return l

class MTBrowsingPageEvent(MTBrowsingEvent):     # Used in subtitles
    """Event corresponding to a new page being loaded"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTBrowsingEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        self.pageIdx = eventInfo[0].split(" - ")[1]
        """Index of the page being loaded (from 0 to 40)"""
        self.pageTitle = eventInfo[0].split(" - ")[2]
        """Title of the page being loaded"""
        self.timeSpentOverall = datetime.timedelta(0, 0, 0)
        """Time spent on the page after this event overall, regardless of interruptions (can only be determined a posteriori, through an analysis)"""
        self.timeSpentWithContent = datetime.timedelta(0, 0, 0)
        """Time spent on the page after this event, minus time spent on questionnaires, watching videos and system pauses (can only be determined a posteriori, through an analysis)"""
        #bondaria -------------------
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

        #----------------------------
        self.relevantToSubgoal = None
        """Is the page relevant for the current subgoal of the user? Possible values: 0 if not, 0.5 if partially relevant, 1 if totally relevant, -1 if N/A (because no subgoal is set for the moment)"""
        self.sub = "Page " + self.pageIdx + " (" + self.pageTitle + ") loaded"

    def getInfo(self, showAll=False, showPageIdx=False, showPageTitle=False, showTimeSpentOverall=False, showTimeSpentWithContent=False, showRelevanceToSubgoal=False, showTimeSpentWithContentImage=False):
    #def getInfo(self, showAll=False, showPageIdx=False, showPageTitle=False, showTimeSpentOverall=False, showTimeSpentWithContent=False, showRelevanceToSubgoal=False):

        l = MTBrowsingEvent.getInfo(self, showAll)
        if showPageIdx or showAll:
            l.append(self.pageIdx)
        if showPageTitle or showAll:
            l.append(self.pageTitle)
        if showTimeSpentOverall or showAll:
            l.append(Event.convertTimeDelta2String(self.timeSpentOverall))
            l.append(self.timeSpentOverall.total_seconds())
        if showTimeSpentWithContent or showAll:
            l.append(Event.convertTimeDelta2String(self.timeSpentWithContent))
            l.append(self.timeSpentWithContent.total_seconds())
        #bondaria--------------------------
        if showTimeSpentWithContentImage:
            #(Overall, WithContent, ImgWithContent, NoImgWithContent, ImgRelWithContent, NoImgRelWithContent, ImgIrrelWithContent, NoImgIrrelWithContent)
            l.append(self.timeSpentOverall.total_seconds())
            l.append(self.timeSpentWithContent.total_seconds())
            #l.append(Event.convertTimeDelta2String(self.timeSpentWithContentImage))
            l.append(self.timeSpentWithContentImage.total_seconds())
            #l.append(Event.convertTimeDelta2String(self.timeSpentWithContentNoImage))
            l.append(self.timeSpentWithContentNoImage.total_seconds())
            # Text + Image vs. Text Only, Rel vs. Irrel
            #l.append(Event.convertTimeDelta2String(self.timeSpentWithContentImageRel))
            l.append(self.timeSpentWithContentImageRel.total_seconds())

            #l.append(Event.convertTimeDelta2String(self.timeSpentWithContentNoImageRel))
            l.append(self.timeSpentWithContentNoImageRel.total_seconds())

            #l.append(Event.convertTimeDelta2String(self.timeSpentWithContentImageIrrel))
            l.append(self.timeSpentWithContentImageIrrel.total_seconds())

            #l.append(Event.convertTimeDelta2String(self.timeSpentWithContentNoImageIrrel))
            l.append(self.timeSpentWithContentNoImageIrrel.total_seconds())
        #----------------------------------
        if showRelevanceToSubgoal or showAll:
            l.append(self.relevantToSubgoal)
        return l

class MTBrowsingImageEvent(MTBrowsingEvent):    # Used in subtitles
    """Event corresponding to an image being viewed"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTBrowsingEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        self.imageName = eventInfo[0].split(" - ")[1]
        """Name of the image being viewed"""
        self.sub = "Image " + self.imageName + " loaded"

    def getInfo(self, showAll=False, showImageName=False):
        l = MTBrowsingEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.imageName])
        else:
            if showImageName:
                l.append(self.imageName)
        return l

class MTBrowsingReadingEvent(MTBrowsingEvent):  # Not used in subtitles
    """Event corresponding to the time spent on the current page being retrieved"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTBrowsingEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        self.timeSpent = eventInfo[1]
        """Time spent on the page (in seconds)"""

    def getInfo(self, showAll=False, showTimeSpent=False):
        l = MTBrowsingEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.timeSpent])
        else:
            if showTimeSpent:
                l.append(self.timeSpent)
        return l

class MTBrowsingVideoEvent(MTBrowsingEvent):    # Not directly used in subtitles (used to build CEvtVideoIsPlaying)
    """Event corresponding to a video being watched"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTBrowsingEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        self.play = eventInfo[0].split("Tutorial ")[1].split(" - ")[0]
        """Type of event, can be Start or End"""
        self.videoName = eventInfo[0].split(" - ")[1]
        """Name of the video being played"""

    def getInfo(self, showAll=False, showVideoName=False, showPlay=False):
        l = MTBrowsingEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.videoName, self.play])
        else:
            if showVideoName:
                l.append(self.videoName)
            if showPlay:
                l.append(self.play)
        return l

class MTBrowsingSessionEvent(MTBrowsingEvent):  # Not used in subtitles
    """Event corresponding to a session ending"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTBrowsingEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        if eventInfo[0] == "Stop":
            self.stopLevel = 1
            """Code associated to the stop (1 for regular stop, 2 for time out)"""
        elif eventInfo[0] == "Session was normally terminated because of time out.":
            self.stopLevel = 2
        else:
            logger.warning("Unknown session event")

    def getInfo(self, showAll=False, showStopLevel=False):
        l = MTBrowsingEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.stopLevel])
        else:
            if showStopLevel:
                l.append(self.stopLevel)
        return l

class MTBrowsingRestoreAfterCrash(MTBrowsingEvent):     # Not used in subtitles
    """Event corresponding to a session restarting after a crash of MetaTutor"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTBrowsingEvent.__init__(self, logger, eventID, absolutetime, timestamp)

class MTBrowsingQuestionnaire(MTBrowsingEvent):
    """Event corresponding to a questionnaire being displayed"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTBrowsingEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        self.questionnaireName = eventInfo[0].split(" - ")[1]
        """Name of the questionnaire being shown"""
        self.status = eventInfo[0].split("Questionnaire ")[1].split(" - ")[0]
        """Type of event, can be Start or End"""
