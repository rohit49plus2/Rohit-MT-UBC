'''
Created on 17 mars 2011

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

from Events.Event import MTEvent

### TYPE 4 EVENTS ###
class MTQuizEvent(MTEvent):                 # Used in subtitles
    """Event occurring every time the user answers to a quiz question, on a page or to finish a subgoal, or to a pretest/posttest question"""
    def __init__(self, logger, eventID, absolutetime, timestamp, eventInfo):
        MTEvent.__init__(self, logger, eventID, 4, absolutetime, timestamp)
        self.styleStart = '<font color="#339900">'
        self.styleEnd = '</font>'
        #: category of question: SRL test (S), Circulatory system test (A) or Page/Subgoal quiz (P)
        if eventInfo[0][0] == "P":
            self.category = "Quiz"
        elif eventInfo[0][0] == "A" or eventInfo[0][0] == "T":  # A for 1.1.x and T for 1.2.x
            self.category = "Circulatory test"
        elif eventInfo[0][0] == "S":
            self.category = "SRL test"
        else:
            logger.warning("Unknown category for a quiz question: " + eventInfo[0][0])
        #: unique ID for a question
        self.questionID = eventInfo[0]
        #: type of answer (Target | Thematic | NearMiss | Unrelated) for quiz, or (A|B|C|D) for test
        self.answerType = eventInfo[1]
        #: is answer correct? (True | False)
        self.answerCorrect = (True if eventInfo[2].lower() == "yes" else False)
        #: how is question related to the content? (text-based | inference) for quiz, or multichoice for test
        self.questionType = eventInfo[3]
        #: ID of the page containing the content to answer correctly to that question (0 for tests)
        self.relatedPage = eventInfo[4]
        self.sub = 'User answered <b>'+ ('' if self.answerCorrect else 'in') + 'correctly</b> (' + self.answerType + ')'

    def getInfo(self, showAll=False, showQuestionCategory=False, showQuestionID=False, showAnswerType=False, showAnswerCorrect=False, showQuestionType=False, showRelatedPage=False):
        l = MTEvent.getInfo(self)
        if showAll:
            l.extend([self.category, self.questionID, self.answerType, self.answerCorrect, self.questionType, self.relatedPage])
        else:
            if showQuestionCategory:
                l.append(self.category)
            if showQuestionID:
                l.append(self.questionID)
            if showAnswerType:
                l.append(self.answerType)
            if showAnswerCorrect:
                l.append(self.answerCorrect)
            if showQuestionType:
                l.append(self.questionType)
            if showRelatedPage:
                l.append(self.relatedPage)
        return l
