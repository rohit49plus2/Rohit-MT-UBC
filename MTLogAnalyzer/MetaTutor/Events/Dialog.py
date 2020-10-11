'''
Created on 14 mars 2011

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

from MetaTutor.Events.Event import MTEvent, MTUnknownEventException

### TYPE 3 EVENTS ###
class MTDialogEvent(MTEvent):   
    def __init__(self, logger, eventID, absolutetime, timestamp):
        MTEvent.__init__(self, logger, eventID, 3, absolutetime, timestamp)

    def getInfo(self, showAll=False):
        l = MTEvent.getInfo(self, showAll)
        return l
    
class MTDialogAgentEvent(MTDialogEvent):
    """Event happening when one of the 4 agents is about to say something to the user"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTDialogEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        self.agentName = eventInfo[0]
        """Name of the agent talking (Gavin, Pam, Mary or Sam)"""
        self.scriptID = eventInfo[1]
        """Identifier of the agent utterance"""
        self.text = eventInfo[2]
        """What the agent is planning on saying (it can be different from what is actually said, since some special values can be dynamically replaced)"""
    
    def getInfo(self, showAll=False, showAgentName=False, showScriptId=False, showText=False):
        l = MTDialogEvent.getInfo(self)
        if showAll:
            l.extend([self.agentName, self.scriptID, self.text])
        else:
            if showAgentName:
                l.append(self.agentName)
            if showScriptId:
                l.append(self.scriptID)
            if showText:
                l.append(self.text)
        return l
        
class MTDialogUserEvent(MTDialogEvent):
    """Event happening when the user is replying to a prompt from an agent or from the system (like clicking on "Continue")"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTDialogEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        if eventInfo[1] != "NA":
            raise MTUnknownEventException("Unknown MTDialogUserEvent value: " + eventInfo[0])
        self.input = eventInfo[2]
        """Input from the user (can be a text typed, the code value associated to the button pressed or the option chosen)"""
    
    def getInfo(self, showAll=False, showUser=False, showInput=False):
        l = MTDialogEvent.getInfo(self)
        if showAll:
            l.extend(["User", self.input])
        else:
            if showUser:
                l.append("User")
            if showInput:
                l.append(self.input)
        return l