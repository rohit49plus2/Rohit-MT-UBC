'''
Created on 17 mars 2011

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

from MetaTutor.Events.Event import MTEvent

### TYPE 6 EVENTS ###
class MTDigimemoEvent(MTEvent):                         # Not directly used in subtitles (used to build CEvtVideoIsPlaying)
    """Event happening everytime the user starts/stops taking notes with the Digimemo note-taking device"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTEvent.__init__(self, logger, eventID, 6, absolutetime, timestamp)
        self.styleStart = '<font color="#0000ff">'
        self.styleEnd = '</font>'
        self.type = eventInfo[0].split("Pen ")[1]
        """Type of the event (can be "pen on" if the user's pen starts touching the pad or "pen off" if it stops)"""
        self.time = eventInfo[1]
        """Time spent since the previous Digimemo event (in microseconds)"""

    def getInfo(self, showAll=False, showType=False, showTime=False):
        l = MTEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.type, self.time])
        else:
            if showType:
                l.append(self.showType)
            if showTime:
                l.append(self.showTime)
        return l