# Script to analyze MT logs and extract basic info from them
# Version: 0.5.2
# Author: F. Bouchet (francois.bouchet@mcgill.ca)
# Date: 2011/10/21

import argparse, sys
import csv
import datetime
from MetaTutor.Log import Logger
from MetaTutorTimeIntervals.MTLogAnalyzer import MTLogAnalyzer
from FaceReader.FRLogAnalyzer import FRLogAnalyzer
from MetaTutor.Events import *
from MetaTutor.Utils import *
#from MetaTutor import Utils
from recordtype import  *  # for recordtype elements, which are mutable version of namedtuples

# launch using the following syntax:
# python loganalyzer.py ./[directory_of_day1&2logs_with_uniform_timestamps]/*.log

AgTalk = []
JSON_MASTER_FILE = "C:/Users/Francois/Documents/Work/McGill/LOGS/MetaTutorSubjectsInfo.json"


def analyzePages(offsetMode, thresholdTime):
    """Analyze the visits on each page for each participants
    (using the fileSubjectsInfo file to load the relevant information)
    and produce two files: one with the number of total visits for each page (in descending order)
    and another with the timestamps for the visits of each page by each participant
    (using the videotime referential if possible, the MetaTutorLogTime referential otherwise)"""
    #: Dictionary counting the number of visits for each page. Elements of the form: {pageNumber, numberOfVisits}.
    cptPages = []
    # Initialize each page counter with 0
    for i in range(0, 41):
        cptPages.append([i, 0])
    # Transforms the list into a dictionary
    cptPages = dict(cptPages)

    #: Dictionary of time differences in seconds between the beginning of the video file and the beginning of the MetaTutor log recording. Elements of the form: {subjectID:[ScreenCaptureOffset,WebcamOnlyOffset]}. A positive offset means MT is launched AFTER the start of the video, which should always be the case.
    timeOffsetSubj = {"33019":[74, 69], "33025":[-1, 117.5], "33038":[-1, 77], "33043":[63, -1], "33056":[-1, 58.5]}
    #FIXME: should use the dictionary in Subject instead of having another one here
    #: List of timestamps when each participant accessed each page. Elements of the form: [[subjectID1, offsetKnown(True/False), [pageNumber1, [timestamp1, ...]], [pageNumber2, [...]], ...], ..., [subjectN, ...]]. The timestamps take into account the offset if it is known.
    timePageSubj = []

    #: Minimum time difference between two pages views for the first one to be considered significant
    minPageViewsTimeDiff = datetime.timedelta(seconds=thresholdTime)

    # Using the subjects info file
    with open("./subjinfo.txt", 'r') as f:
        fcsv = csv.reader(f, delimiter=',')
        # for each subject from the file
        for subjectLine, subject in enumerate(fcsv):
            i = 0
            # Initialize the list of timestamps for this participant
            curTimePageSubj = []
            for pageNb in range(0, 41):
                curTimePageSubj.append([pageNb, []])
            # Add the participant number and the referential for the timestamps (either "MetaTutor" or "Video")
            curTimePageSubj.insert(0, subject[0])
            # Initialize the offset to get into the video referential for timestamps, if the value is available
            if subject[0] in timeOffsetSubj:
                curOffsetSubj = datetime.timedelta(seconds=timeOffsetSubj[subject[0]][offsetMode])
                #curOffsetKnown = True
                if (offsetMode == 0):
                    curTimePageSubj.insert(1, "ScreenCapture time referential")
                else:
                    curTimePageSubj.insert(1, "Webcam only time referential")
            else:
                curOffsetSubj = datetime.timedelta(seconds=0)
                #curOffsetKnown = False
                curTimePageSubj.insert(1, "MetaTutor time referential")

            # Initialize those two values to prevent an error message, whenever precautions are taken not to use them before their real initialization
            pageIdx = 0
            prevTimeStamp = 0
            # Retrieve the (page, timestamps) elements to insert them properly in curTimePageSubj, and count the pages in cptPages
            if (subjectLine != 0):  # ignore the title line
                for elt in subject[2:]:
                    if (i % 2) == 0:  # first element is page number
                        if i > 1:
                            prevPageIdx = pageIdx               # save the previous page index
                        pageIdx = int(elt.split(" - ")[1])      # get the page index
                        cptPages[pageIdx] += 1                  # increment the counter corresponding to the current page
                    else:           # second element is corresponding to the timestamp
                        curTimeStamp = datetime.datetime.strptime(str(elt) + "000", "%H:%M:%S.%f")     # generate a time structure from the text of the timestamp
                        #print type(curTimeStamp)
                        #curTimeStamp = datetime.time(*curTimeStamp[0:6])                        # convert it into a datetime
                        #print curTimeStamp
                        #print time.mktime(curTimeStamp)
                        #curTimeStamp2 = datetime.fromtimestamp(time.mktime(curTimeStamp))        # convert it into a datetime
                        #curTimeStamp3 = datetime.time()                                          # convert it into a time object (of the datetime module), != time structure
                        curTimeStamp = curTimeStamp + curOffsetSubj                                   # add the potential offset
                        #print curTimeStamp
                        if i > 1:
                            if ((curTimeStamp - prevTimeStamp) < minPageViewsTimeDiff):             # the new page is loaded too soon after the previous one for the previous one to really matter
                                cptPages[prevPageIdx] -= 1                                                  # decrement the counter for the previous page
                                curTimePageSubj[prevPageIdx + 2][1] = curTimePageSubj[prevPageIdx + 2][1][:-1]  # delete the timestamp of the previous page

                        prevTimeStamp = curTimeStamp                                                # save the previous timestamp
                        curTimeStamp = datetime.datetime.strftime(curTimeStamp, "%H:%M:%S.%f")[:12]  # regenerate a new text timestamp

                        curTimePageSubj[pageIdx + 2][1].append(curTimeStamp)                          # pageIdx+2 as there are 2 elements stored at the beginning of the list that are not pages (subjectID and offset)


                    i += 1
            # Add information about the current subject into the general list
            timePageSubj.append(curTimePageSubj)
    print timePageSubj

    #: Number of visits per page, reformatted in a human-friendlier way
    cptPagesFormated = []
    for idx, i in enumerate(cptPages.values()):
        cptPagesFormated.append([i, "Page " + str(idx)])
    cptPagesFormated.sort()
    cptPagesFormated.reverse()
    print cptPagesFormated

    # Save information about global page views into a file
    with open("./pageinfo.txt", 'wb') as f:
        writer = csv.writer(f, dialect='excel')
        for page in cptPagesFormated:
            writer.writerow(page)
    # Save information about timestamps of page view per subject into a file
    with open("./pageSubjTime.txt", 'wb') as f:
        writer = csv.writer(f, dialect='excel')
        for subject in timePageSubj[1:]:
            for pageInfo in subject[2:]:
                tmp = [subject[0], subject[1], "Page " + str(pageInfo[0])]
                tmp.extend(pageInfo[1:][0])
                writer.writerow(tmp)

if __name__ == "__main__":
#    tmpIgnoreThis = False        # temporary variable to ignore the part of goal setting that fails for now

    # Configure the parser for arguments given to the program
    parser = argparse.ArgumentParser(prog='MTLogAnalyzer', description='Analyzer for MetaTutor events logs')
    #parser.add_argument('logspath', metavar='PATH', type=str, nargs=1, default=".\\", help="path of a directory containing the MT logs (without -r) or containing the summary of a previous analysis of MT logs (with -r)")
        #parser.add_argument('-s', '--spss', action='store_true', help="")
    # -- MT logs related arguments
    parser.add_argument('-m', '--mtlogspath', action='store', type=str, nargs=1, default=None, help="path of a directory containing the MT logs (replace -r)")
    parser.add_argument('-s', '--summarymtlogspath', action='store', type=str, nargs=1, default=None, help="retrieve data from a previously done analysis of the MT logs, instead of parsing them (replace -m)")
    # -- FR logs related arguments
    parser.add_argument('-f', '--frlogspath', action='store', type=str, nargs=1, default=None, help="path of a directory containing the FR logs")
    parser.add_argument('-e', '--frcustomemos', action='store_true', help="while processing FaceReader logs, also calculate custom dominant emotions (on instant and on duration) using our own algorithm mimicking Noldus' one, and provide information about the agreement")
    parser.add_argument('-o', '--froffsetfile', action='store', type=str, nargs=1, default=None, help="path and name of the CSV file containing video offset times used to align FR and MT logs")
    # -- saving information related arguments
    parser.add_argument('-p', '--pickle', action='store_true', help="generate .pkl files for each analyzed participants not to have to parse logs again")
    parser.add_argument('-j', '--generateJSONfile', action='store_true', help="generate a JSON file with the location of log files for the participants analyzed")

    args = parser.parse_args()

    # Configure the logging with the level of messages to be displayed: debug, info, warning or error
    logger = Logger("info").logger
    #confLog("debug")
    #logger = Logger.logger

    # Creation of an analyzer, based on the log files
    readSummary = False if args.summarymtlogspath == None else True
    if args.mtlogspath != None:
        mtlogspath = args.mtlogspath[0]
    elif args.summarymtlogspath != None:
        mtlogspath = args.summarymtlogspath[0]
    else:
        logger.error("A path to MT logs needs to be provided using either -m or -s")
        sys.exit(-1)
    mtla = MTLogAnalyzer(logger, readSummary, args.generateJSONfile, args.pickle, mtlogspath)# subjectsIDToDebug=["23072"]#, maxFilesToConsider=2)#, "SRLbysubj.txt")

    # Creation of an analyzer for FaceReader logs
    if args.frlogspath != None:
        if args.froffsetfile == None:
            logger.error("An offset file must be provided in order to use FaceReader as a data channel - this channel won't be used for any analysis")
        else:
            frla = FRLogAnalyzer(logger, [subj.ID for subj in mtla.subjects], args.frlogspath[0], args.frcustomemos, args.froffsetfile[0])
            # frla.parseSubjects()
            frla.associateEmotionsToSubjectEvents(mtla.subjects)
            # the logs for each subjects aren't parsed at this step but on need because of the room taken in memory if trying to load FR logs for many subjects
    else:
        logger.warning("No FaceReader root path has been provided - this channel won't be used for any analysis")

    # Print subjects information
    #print mtla.getSubjectsSetInfoString()
    # SRL only
    #print mtla.getSubjectsInfoString(subjectData=False, experimentData=False, pageData=False, eventsData=False, SRLData=True)
    # Print information about the SRL events for subjects
    #mtla.printSubjectsUniqueSRL(Rule.MTRuleSRLUnknownEvent)

    # TODO: separate the reading from the CSV file from being in analyzePages, to become part of the second half of the init of MTLogAnalyzer
    offsetMode = 1      # 0 = ScreenCapture, 1 = Webcam only

    # Make timestamps for each page for each participant
#    thresholdTime = 5   # in seconds - minimum time to make checking a page considered relevant (below that, a page viewed is ignored)
#    analyzePages(offsetMode, thresholdTime)

    # Make a subtitle file
    # Subject X: 93 = 33019
    # Subject Y: 109 = 33038  (en offsetMode 1)
    # Subject Z: 114 = 33043  (en offsetMode 0)
    # Subject A: 96 = 33025   (en offsetMode 1)
    # Subject B: -2 = 33056   (en offsetMode 1)
#    subjID = -2
    #for subjID in range(1,117):
#    logger.info("Treating subject: " + str(mtla.subjects[subjID].ID))
#    sub = mtla.subjects[subjID].makeSubtitles(logger,subjects[subjID],offsetMode)
#    print sub


    # 23051 = 48
    # 33001 = 77
    # 33006 = 82
    # Get events of a given type for everyone
    #for i, subj in enumerate(mtla.subjects):
    #    if i>=0: # from subject n
    #        logger.info("Treating subject: " + str(subj.ID))
    #        subj.getEventListAsString([Custom.CEvtSubgoalSet, Custom.CEvtPursuingNewSubgoal, Custom.CEvtPursuingSameSubgoal])

    # Generate info for IVA article
    #for i, subj in enumerate(mtla.subjects):
    #    logger.info("Treating subject: " + str(subj.ID))
    #    subj.getEventListAsString([Custom.CEvtSubgoalSet, Dialog.MTDialogAgentEvent, Dialog.MTDialogUserEvent])#, Custom.CEvtPursuingNewSubgoal, Custom.CEvtPursuingSameSubgoal])

    dictDataToAnalyze = { "JOL":["JOLQuiz.csv", 2, [[Custom.CEvtUserJudgingLearningJOL, {"showUnderstandingLevel":True, "showInitiative":True}], [Custom.CEvtUserTakingQuiz, {}]]],
                                    "FOK":["FOKQuiz.csv", 2, [[Custom.CEvtUserFeelingKnowledgeFOK, {"showKnowledgeLevel":True, "showInitiative":True}], [Custom.CEvtUserTakingQuiz, {}]]],
                                    "CE":["CE.csv", 2, [[Custom.CEvtUserEvaluatingContentCE, {"showEvaluatedRelevance":True, "showRealRelevancy":True, "showInitiative":True}]]],
                                    "Tests":["PrePostTest.csv", 0, [[Custom.CEvtUserTakingPreTest, {"showScore":True}], [Custom.CEvtUserTakingPostTest, {"showScore":True}], [Quiz.MTQuizEvent, {"showAll":True}]]],
                                    "IVA":["IVA.csv", 2, [[Custom.CEvtSubgoalSet, {}], [Dialog.MTDialogUserEvent, {}], [Dialog.MTDialogAgentEvent, {"showAgentName":True, "showScriptId":True}], [Agent.MTAgentTalkEvent, {}]]],   # info for the IVA article
                                    "Subgoals":["SG.csv", 2, [[Custom.CEvtSubgoalSet, {}], [Custom.CEvtPursuingNewSubgoal, {}], [Custom.CEvtPursuingSameSubgoal, {}]]],
                                    "Pages":["Pages.csv", 2, [[Browsing.MTBrowsingPageEvent, {}]]],
                                    "SummaryInitiative":["SummInit.csv", 2, [[Custom.CEvtNoteAddedFromSummary, {}], [Custom.CEvtNoteNotAddedFromSummary, {}], [Custom.CEvtUserTypingSummary, {"showInitiative":True}]]],
                                    "SRLTest":["SRLTest.csv", 1, [[Custom.CEvtUserTakingSRLTest, {"showScore":True}]]],
                                    "PageRelevance":["PageRelevance.csv", 2, [[Browsing.MTBrowsingPageEvent, {"showPageIdx":True, "showTimeSpentWithContent":True, "showRelevanceToSubgoal":True}]]],
                                    "Questionnaires":["Questionnaires.csv", 2, [[Custom.CEvtQuestionnaireOngoing, {"showQuestionnaireName":True}], [Layout.MTLayoutEvent, {"showLayout":True}]]],
                                    "QuestionnaireEV":["EV.csv", 2, [[Questionnaire.MTQuestionnaireEIV, {"showAll":True}]]],
                                    "Layouts":["Layouts.csv", 2, [[Layout.MTLayoutEvent, {"showLayout":True}]]],
                                    "Images":["Images.csv", 2, [[Browsing.MTBrowsingImageEvent, {"showImageName":True}]]],
                                    "Rules":["Rules.csv", 2, [[Rule.MTRuleSRLEvent, {"showRule":True, "showInitiative":True, "showStartingAction":True}]]],
                                    "Quiz":["Quiz.csv", 2, [[Quiz.MTQuizEvent, {"showAll":True}]]],
                                    "Quizzes":["Quizzes.csv", 2, [[Custom.CEvtUserTakingQuiz, {"showAll":True}]]],
                                    "AgentSpeaking":["AgentSpeaking.csv", 2, [[Custom.CEvtAgentSpeaking, {"showAll":True}], [Agent.MTAgentTalkEvent, {"showScriptId":True, "showType":True}]]],   # only file for now to have absolute time for custom events (as of Jan. 2013)
                                    # Useful for AOI extraction
                                    "MetaRules":["MetaRules.csv", 2, [[MetaRule.MTMetaRuleEvent, {"showAll":True}]]],
                                    "Custom":["Custom.csv", 0, ""],
                                    # General stats (SRL processes, scores, etc.)
                                    "PagesRelInitSG":["PagesRelInitSG.csv", 0, ""],
                                    "PagesTimeInform":["PagesTimeInform.txt", 2, [[Browsing.MTBrowsingPageEvent,{}]]],
                                    #----bondaria
                                    #"Daria-PageTime":["Daria-PageTime.txt", 2, [[Browsing.MTBrowsingPageEvent,{"showTimeSpentWithContent":True, "showTimeSpentOverall":True}]]],
                                    "Daria-PageTime":["Daria-PageTime.txt", 2, [[Browsing.MTBrowsingPageEvent,{"showTimeSpentWithContentImage": True, "showPageIdx": True}]]],
                                    "Daria-Trial": ["Daria-TrialSG.txt", 2, ""],
                                    "UBCActionsFeatures": ["ActionFeatures.csv",2, ""],
                                    "UBCActionsFeaturesNoCorrel": ["ActionFeaturesNoCorrel.csv",2, ""],
                                    #-------
                                    "NatashaActionFeatures":["NatashaActionFeatures.csv",2,""]
                                }   # name:[filename, day (0 for both), [[Event, {fieldName:True/False}], ...]]]

    dataToAnalyze = "QuestionnaireEVAnalysis"
    #dataToAnalyze = "PagesRelInitSG"
    #dataToAnalyze = "PagesTimeInform"
    #dataToAnalyze = "Daria-PageTime"
    #dataToAnalyze = "UBCActionsFeatures"
    dataToAnalyze = "UBCActionsFeaturesNoCorrel"
    dataToAnalyze = "NatashaActionFeatures"
    # Possible values:
    # 1. Dump of events: JOL, FOK, CE, Tests, IVA, Subgoals, Pages, SummaryInitiative, SRLTest, PageRelevance, Questionnaires, Layouts, Images, Custom, PagesRelInitSG,
    # 2. Advanced analysis: PageSGAnalysis, NoteTakingAnalysis, SRLperPageAnalysis...
    data = ""
    rows = []
    if dataToAnalyze == "":
        logger.info("No data analysis requested")
    else:
        logger.info("Data analysis requested: " + dataToAnalyze)
        if dataToAnalyze == "PageSGAnalysis":
            # Get pages and if they are relevant for current subgoal for Reza
            res = mtla.analyzePageViewsAndRelevance()
            Utils.exportString2Excel(res, "PageSGAnalysis.txt")
            dataToAnalyze = ""  # no need for further analysis

        elif dataToAnalyze == "SRLperPageAnalysis":
            res = mtla.analyzeSRLperPage()
            Utils.exportList2Excel(res, "SRLperPageAnalysis.csv")
            dataToAnalyze = ""  # no need for further analysis

        elif dataToAnalyze == "NoteTakingAnalysis":
            # Get notes-related events for everyone for Melissa
            res = mtla.analyzeNotes()
            Utils.exportString2Excel(res, "NoteTakingAnalysis.txt")
            dataToAnalyze = ""  # no need for further analysis

        elif dataToAnalyze == "CoRLAnalysis":
            # Get data for CoRL study for Jason
            res = mtla.getInitialSubgoalSettingSequence()
            Utils.exportList2Excel(res, "CoRL.csv")
            dataToAnalyze = ""  # no need for further analysis

        elif dataToAnalyze == "EyetrackingCOISAnalysis":
            # Merge information from eyetracking log with MetaTutor log to study COIS for Greg & Reza's EARLI paper
            res = mtla.analyzeCOIS()
            Utils.exportString2Excel(res, "COIS.csv")
            dataToAnalyze = ""  # no need for further analysis

        elif dataToAnalyze == "PageInterruptionsAnalysis":
            # Get data on interruptions for Anoop's EARLI paper
            for i, subj in enumerate(mtla.subjects):
                logger.info("Treating subject " + str(subj.ID) + "...")
                mtla.subjects[i].computeExtraAttributes(logger, mtla.nonValidTestQuestions, mtla.nbSubgoalsSetInitially, mtla.nbPagesInSystem, mtla.matTestPageDict, mtla.matPageSubgoalDict, mtla.minNoteTime)
            res = mtla.analyzePageInterruptions(logger)
            Utils.exportString2Excel(res, "PageInterruptions.csv")
            dataToAnalyze = ""  # no need for further analysis

        elif dataToAnalyze == "QuestionnaireEVAnalysis":
            mtla.analyzeEV("./data/questionnaires/EV-study4.csv")  # parameter = location of the EV data
            dataToAnalyze = "QuestionnaireEV"

        elif dataToAnalyze == "MetaRulesAnalysis":
            for i, subj in enumerate(mtla.subjects):
                logger.info("Treating subject " + str(subj.ID) + "...")
                mtla.subjects[i].computeExtraAttributes(logger, mtla.nonValidTestQuestions, mtla.nbSubgoalsSetInitially, mtla.nbPagesInSystem, mtla.matTestPageDict, mtla.matPageSubgoalDict, mtla.minNoteTime)
            res = mtla.analyzeMetaRules(5, ["hyper1", "hyper2"]) # for study 4.5 AIED paper
            Utils.exportList2Excel(res, "MetaRulesAnalysis.csv")
            dataToAnalyze = ""  # no need for further analysis

        elif dataToAnalyze == "DM":
            ### Get data for HMM
            # 1: QuizSeparateNAndP:
            #    - True: QuizP and QuizN
            #    - False: Quiz only             (default)
            # sample:
            #    - good&badLearners: for participants defined as "good" and "bad" learners, uniquely according to the difference pre/postTest
            #    - 3clusters: for participants separated as members of the 3 clusters defined in JEDM
#            mtla.getEventListSequenceForDataMining(sample="cluster2HvsOthers",
#                                                   mergeSequenceOfSameActionAsMult=True,
#                                                   groupAllSRLProcesses=False,
#                                                   QuizSeparateNAndP=True,
#                                                   separateMonitoringProcessAccordingToRelevanceEstimation=True,
#                                                   separateReadAccordingToRelevance=True,
#                                                   separateReadAccordingToDuration=True,
#                                                   readLongShortThreshold=15)
            mtla.getEventListSequenceForDataMining(sample="cluster2HvsOthers",
                                                   mergeSequenceOfSameActionAsMult=False,
                                                   groupAllSRLProcesses=False,
                                                   QuizSeparateNAndP=True,
                                                   separateMonitoringProcessAccordingToRelevanceEstimation=True,
                                                   separateReadAccordingToRelevance=True,
                                                   separateReadAccordingToDuration=True,
                                                   readLongShortThreshold=15)
            dataToAnalyze = ""  # no need for further analysis
        if dataToAnalyze != "":     # it can have been set since the last check
            # Simply treat each subject and extract the events requested
            for i, subj in enumerate(mtla.subjects):
                logger.info("Treating subject " + str(subj.ID) + "...")
                mtla.subjects[i].computeExtraAttributes(logger, mtla.nonValidTestQuestions, mtla.nbSubgoalsSetInitially, mtla.nbPagesInSystem, mtla.matTestPageDict, mtla.matPageSubgoalDict, mtla.minNoteTime)
                if dataToAnalyze == "Custom":
                    rowTypesToExport = ["ID", "subject", "tests", "times", "subgoals", "quizzesSubgoal", "quizzesPage", "notes", "SRLEvents"]
                    # Possible values:
                    # "ID", "subject", "experiment", "tests", "times", "subgoals", "quizzesSubgoal", "quizzesPage", "notes", "pagesViewEvents", "allEvents", "SRLEvents"
                    if rows == []:
                        rows = [subj.getSummaryRowList(logger, rowTypesToExport, [], True)]
                    rows.append(subj.getSummaryRowList(logger, rowTypesToExport, [], False))
                    print rows[-1]
                    Utils.exportList2Excel(rows, "CustomFix.csv") #dictDataToAnalyze[dataToAnalyze][0])
                elif dataToAnalyze == "PagesRelInitSG":
                    if rows == []:
                        rows = [subj.getSummaryRowList(logger,["ID", "pagesRelInitSG"], [], True)]
                    rows.append(subj.getSummaryRowList(logger,["ID", "pagesRelInitSG"], [], False))
                    Utils.exportList2Excel(rows, dictDataToAnalyze[dataToAnalyze][0])

                #bondaria-------

                elif dataToAnalyze == "Daria-Trial":
                    #print "Subject Duration Pages Relevant Subgoal Were Open ",  subj.pagesTotalTimeSpentRelevantSG
                    #print "Reading duration: ", subj.readingDuration
                    #print "Total duration user spent with content: ", subj.pagesTotalTimeSpentWithContent
                    #print "Percentage of time spent on reading: ", subj.pagesTimeProportionSGRel
                    #print "Time spent setting SG: ", subj.SGTimeTotal
                    #print "Time spent setting SG AVG: ", subj.SGTimeAVG
                    #print "Number of subgoals set during the session: ", subj.NbSGTotal
                    if rows == []:
                        rows = [subj.getSummaryRowList(logger,["ID", "Durations"], [], True)]
                    rows.append(subj.getSummaryRowList(logger,["ID", "Durations"], [], False))
                    Utils.exportList2Excel(rows, "test.csv")
                #-------------
                elif dataToAnalyze == "UBCActionsFeatures":
                    #print "Printing features for UBC Actions Features"
                    if rows == []:
                        rows = [subj.getSummaryRowList(logger,["ID", "ActionsFeatures"], [], True)]
                        with open("listoffeatures.txt","w") as f:
                            for el in rows[0]:
                                f.write(el +"\n")

                    rows.append(subj.getSummaryRowList(logger,["ID", "ActionsFeatures"], [], False))
                    Utils.exportList2Excel(rows, dictDataToAnalyze[dataToAnalyze][0])
                #bondaria
                elif dataToAnalyze == "UBCActionsFeaturesNoCorrel":
                    #print "Printing features for UBC Actions Features (no correlation)"
                    if rows == []:
                        rows = [subj.getSummaryRowList(logger,["ID", "ActionsFeaturesNoCorrel"], [], True)]
                        with open("listoffeaturesNoCorrel.txt","w") as f:
                            for el in rows[0]:
                                f.write(el +"\n")

                    rows.append(subj.getSummaryRowList(logger,["ID", "ActionsFeaturesNoCorrel"], [], False))
                    Utils.exportList2Excel(rows, dictDataToAnalyze[dataToAnalyze][0])

                elif dataToAnalyze == "NatashaActionFeatures":
                    #print "Printing features for UBC Actions Features (no correlation)"
                    if rows == []:
                        rows = [subj.getSummaryRowList(logger,["ID", "Group", "subject", "times", "subgoals", "notes", "SRLEvents", "NatashaDariaFeatures"], [], True)]
                        with open("listofNatashaFeatures.txt","w") as f:
                            for el in rows[0]:
                                f.write(el +"\n")

                    rows.append(subj.getSummaryRowList(logger,["ID", "subject", "times", "subgoals", "notes", "SRLEvents", "NatashaDariaFeatures"], [], False))
                    Utils.exportList2Excel(rows, dictDataToAnalyze[dataToAnalyze][0])

                else:
                    print "No predefined format. Processing as usual."
                    data += subj.getEventListAsString(dictDataToAnalyze[dataToAnalyze][2], dictDataToAnalyze[dataToAnalyze][1])
                    Utils.exportString2Excel(data, dictDataToAnalyze[dataToAnalyze][0])

    # Display all the talk from a given agent
    #AgTalk = list(set(AgTalk))
    #AgTalk.sort()
    #for e in AgTalk:
    #    print e

    #TODO: check Custom.CEvtUserTypingSummary, got some Warning: unknown value for knowledge level: (followed by a text)


    logger.info("Program finished normally")
