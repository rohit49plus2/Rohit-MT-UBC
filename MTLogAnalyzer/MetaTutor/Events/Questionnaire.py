'''
Created on May 29, 2012

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

from MetaTutor.Events.Event import MTEvent, Event

### Independent subcategory of Type 1 events ###
class MTQuestionnaire(MTEvent):
    '''Event happening when a measure questionnaire is shown in MetaTutor interface'''
    def __init__(self, logger, eventID, absolutetime, timestamp):
        '''Default questionnaire constructor'''
        MTEvent.__init__(self, logger, eventID, 1, absolutetime, timestamp, "Browse")
        
    def getInfo(self, showAll=False):
        l = MTEvent.getInfo(self, showAll)
        return l
    
class MTQuestionnaireAGQ(MTQuestionnaire):
    '''Event happening when the Academic Goal Questionnaire is shown at the beginning of day 2'''
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTQuestionnaire.__init__(self, logger, eventID, absolutetime, timestamp)
        
        
class MTQuestionnaireEIV(MTQuestionnaire):
    '''Event happening when the Emotions Interests and Values questionnaire is shown, several times during day 2'''
    def __init__(self, logger, eventID, absolutetime, timestamp):
        MTQuestionnaire.__init__(self, logger, eventID, absolutetime, timestamp)
        self.emoHappy = -1
        self.emoEnjoyment = -1
        self.emoHope = -1
        self.emoPride = -1
        self.emoAnger = -1
        self.emoFrustration = -1
        self.emoAnxiety = -1
        self.emoFear = -1
        self.emoShame = -1
        self.emoHopelessness = -1
        self.emoBoredom = -1
        self.emoSurprise = -1
        self.emoContempt = -1
        self.emoDisgust = -1
        self.emoConfusion = -1
        self.emoCuriosity = -1
        self.emoSadness = -1
        self.emoEureka = -1
        self.emoNeutral = -1
        self.valueTask = -1
        
    def setQuestionnaireReplies(self, row):
        """Set the values of each of the 20 items measured by the EV, provided in the order of the questionnaire (i.e. as collected in Google Docs)"""
        if len(row) != 20:
            self.logger.error("Invalid number of items provided for an EV (should be 20): " + len(row))
        [self.emoHappy, self.emoEnjoyment, self.emoHope, self.emoPride, self.emoAnger, self.emoFrustration, self.emoAnxiety, self.emoFear, self.emoShame, 
                      self.emoHopelessness, self.emoBoredom, self.emoSurprise, self.emoContempt, self.emoDisgust, self.emoConfusion, self.emoCuriosity, self.emoSadness, 
                      self.emoEureka, self.emoNeutral, self.valueTask] = row
    
    def getInfo(self, showAll=False, showEmotions=False, showValue=False):
        l = MTQuestionnaire.getInfo(self, showAll)
        if showAll:
            l.extend([self.emoHappy, self.emoEnjoyment, self.emoHope, self.emoPride, self.emoAnger, self.emoFrustration, self.emoAnxiety, self.emoFear, self.emoShame, 
                      self.emoHopelessness, self.emoBoredom, self.emoSurprise, self.emoContempt, self.emoDisgust, self.emoConfusion, self.emoCuriosity, self.emoSadness, 
                      self.emoEureka, self.emoNeutral, self.valueTask])
        else:
            if showEmotions:
                l.extend([self.emoHappy, self.emoEnjoyment, self.emoHope, self.emoPride, self.emoAnger, self.emoFrustration, self.emoAnxiety, self.emoFear, self.emoShame, 
                          self.emoHopelessness, self.emoBoredom, self.emoSurprise, self.emoContempt, self.emoDisgust, self.emoConfusion, self.emoCuriosity, self.emoSadness, 
                          self.emoEureka, self.emoNeutral])
            if showValue:
                l.append(self.valueTask)
        return l