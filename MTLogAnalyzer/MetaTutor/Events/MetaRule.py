'''
Created on 2013-01-28

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

from MetaTutor.Events.Event import MTEvent, MTUnknownEventException

### TYPE 9 EVENTS ###
class MTMetaRuleEvent(MTEvent):
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTEvent.__init__(self, logger, eventID, 9, absolutetime, timestamp)
        self.metaruleId = eventInfo[0].split("Metarule (")[1].split(")")[0]
        """ID of the metarule executed"""
        self.ruleName = eventInfo[0].split("applied to ")[1].split(": ")[0]
        """Name of the rule affected by the metarule"""
        self.initiative = "user" if "user value" in eventInfo[0] else "system"
        """What part of the percentage of activation is affected (user or system)"""
        self.previousValue = float(eventInfo[0].split("from ")[1].split(" to")[0])
        """Previous percentage of chance of activation of the rule"""
        self.newValue = float(eventInfo[0].rsplit("to ")[2].split(" (")[0])
        """New percentage of chance of activation of the rule"""
        self.changeValue = float(eventInfo[0].split("by ")[1].split(" from")[0])
        """Number of points changed between previous and new percentage of chance of activation"""
        if "decremented" in eventInfo[0]:
            self.changeValue = -1*self.changeValue
        
    def getInfo(self, showAll=False):
        l = MTEvent.getInfo(self, showAll)
        if showAll:
            l.extend([self.metaruleId, self.ruleName, self.initiative, self.previousValue, self.changeValue, self.newValue])
        return l
    
