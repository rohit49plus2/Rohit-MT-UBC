'''
Created on 14 mars 2011

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

from MetaTutor.Events.Event import MTEvent, MTUnknownEventException

### TYPE 8 EVENTS ###
class MTAgentEvent(MTEvent):
    def __init__(self, logger, eventID, absolutetime, timestamp):
        MTEvent.__init__(self, logger, eventID, 8, absolutetime, timestamp)
        
    def getInfo(self, showAll=False):
        l = MTEvent.getInfo(self, showAll)
        return l

class MTAgentTalkEvent(MTAgentEvent):
    """Event happening when one of the 4 agents is actually starting/finishing to say something out loud (with the TTS)"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTAgentEvent.__init__(self, logger, eventID, absolutetime, timestamp)
        self.agentName = eventInfo[0]
        """Name of the agent talking (Gavin, Pam, Mary or Sam)"""
        self.scriptID = eventInfo[1]
        """Identifier of the agent utterance"""
        self.text = ""
        """What is actually said by the agent (several variations exist for a given utterance and special values can be dynamically replaced)"""
        if (eventInfo[2] == "Start" or eventInfo[2] == "Stop"):
            self.type = eventInfo[2]
            if (eventInfo[2] == "Start"):
                self.text = eventInfo[3]
        else:
            raise MTUnknownEventException("Unknown MTAgentTalkEvent value: ", eventInfo[2])
        
    def getInfo(self, showAll=False, showAgentName=False, showScriptId=False, showType=False, showText=False):
        l = MTAgentEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.agentName, self.scriptID, self.type, self.text])
        else:
            if showAgentName:
                l.append(self.agentName)
            if showScriptId:
                l.append(self.scriptID)
            if showType:
                l.append(self.type)
            if showText:
                l.append(self.text)
        return l