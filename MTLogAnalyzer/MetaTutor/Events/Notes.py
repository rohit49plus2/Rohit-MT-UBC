'''
Created on 17 mars 2011

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

from MetaTutor.Events.Event import MTEvent

### TYPE 5 EVENTS ###
class MTNoteEvent(MTEvent):
    """Event happening every time the user has finished taking notes through the embedded note-taking interface"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTEvent.__init__(self, logger, eventID, 5, absolutetime, timestamp)
        self.styleStart = '<font color="#0000ff">'
        self.styleEnd = '</font>'
        self.noteType = eventInfo[0]
        """Type of notes (always worth 1 apparently)"""
        self.pageID = eventInfo[1]
        """ID of the page the user was viewing while taking notes"""
        self.content = eventInfo[2]
        """The note the user has actually typed"""
        
    def getInfo(self, showAll=False, showNoteType=False, showPageId=False, showContent=False):
        l = MTEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.noteType, self.pageID, self.content])
        else:
            if showNoteType:
                l.append(self.noteType)
            if showPageId:
                l.append(self.pageID)
            if showContent:
                l.append(self.content)
        return l