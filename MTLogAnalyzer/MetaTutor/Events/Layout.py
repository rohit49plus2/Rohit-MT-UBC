'''
Created on 14 mars 2011

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

from MetaTutor.Events.Event import MTEvent

### TYPE 7 EVENTS ###
class MTLayoutEvent(MTEvent):
    """Punctual event when the GUI layout of the application is changing on screen"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTEvent.__init__(self, logger, eventID, 7, absolutetime, timestamp)
        self.styleStart = '<font color="#0000ff">'      # used for Note taking events
        self.styleEnd = '</font>'
        self.layout = eventInfo[0]
        """Name of the layout now being shown (can be one of the seven following values: 
        TutorialVideo, InputNoContent, InputWithContent, InputEnlarged, Normal, FullView, Notes
        as well as Pause"""
        
    def getInfo(self, showAll=False, showLayout=False):
        l = MTEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.layout])
        else:
            if showLayout:
                l.append(self.layout)
        return l