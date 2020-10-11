'''
Created on 2013-02-15

@author: F. Bouchet (francois.bouchet@mcgill.ca)
'''

import csv, sys
from datetime import timedelta

class FRLogParser(object):
    '''
    classdocs
    '''
    frdetStartEvent = "Video Time"                             # first relevant element to consider in the FR detailed logfile
    frstaStartEvent = "Video Time"                              # first relevant element to consider in the FR state logfile
    dictColIdx = {}                                                    # dictionary of columns available where key represents the column name and its associated value is an integer corresponding to the index of this column (starting with column 0)
    secEmotLimit = 0.01                                            # threshold to consider an emotion as relevant

    def __init__(self):
        '''
        Constructor
        '''
    
    def initColumnIndexes(self, titles):
        self.dictColIdx = {}
        for idx, title in enumerate(titles):
            self.dictColIdx[title] = idx
    
    def parseLogs(self, logger, subject, computeCustomEmotions=False):
        newlog = []                                                     # the list that will contain the new log
            
        ###
        ### STEP 1: extract important information from the detailed FR log file
        ###
        cut = True
        i = 0
        with open(subject.detailedLog, 'rU') as f:                # open the detailed FR logfile
            frdetlog = csv.reader(f, delimiter='\t')                # and parse it as a CSV file with tabulations 
    
            for row in frdetlog:
                if cut:
                    if len(row)>=1:                         # we skip the beginning of the file
                        if row[0] == self.frdetStartEvent:   # until we find the starting pattern
                            cut = False
                            # check if there is a column for valence (& quality) or just emotions
                            self.initColumnIndexes(row)
                            valenceQualityIncluded = "Valence" in self.dictColIdx
                            logger.info("\tValence & Quality included: " + str(valenceQualityIncluded))
                if not cut:
                    i+=1
                    if i == 3:    # Retrieve the number of frames per second in the video based on the value of the milliseconds in the second line of the FR detailed log
                        msStep = row[0][-3:]
                        #print str(math.floor(1000.0/int(msStep))) 
                        logger.info("\t{0:.2f} fps".format(1000.0/int(msStep)))
                        subject.fps = 1000.0/int(msStep)
                        deltatime = timedelta(microseconds=int(msStep)*1000)
                        emoAppPersistence = (500/int(msStep)) + 1
                        emoDisapPersistence = emoAppPersistence * 2
                    if row[0] != '':                            # to avoid problems with last line of files, which sometimes isn't fully filled
                        newrow = row[0:8]                # keep the 8 first relevant columns (timetag, 7 emotions)
                        if valenceQualityIncluded:        # add valence and quality if they are there
                            newrow.append(row[self.dictColIdx["Valence"]])
                            newrow.append(row[self.dictColIdx["Quality"]])
                        newlog.append(newrow)       
#        print "STEP 1"
#        print newlog[0]
#        print newlog[1]
        
        ###
        ### STEP 2: retrieve the dominant emotional state from FR state log file,
        ### and insert it on the corresponding lines
        ###
        latestEmo = ""
        with open(subject.stateLog, 'r') as f:                     # open the state FR logfile
                frstalog = csv.reader(f, delimiter='\t')                # and parse it as a CSV file with tabulations
                for row in frstalog:
                        if len(row)>=1:                                 # skip the beginning of the file
                                if row[0] == self.frstaStartEvent:           # until the starting pattern is found
                                        nextEmo = row                   # then set the first emotion we'll need to introduce in the logfile
                                                                        # (nextEmo is of the form [timestamp, emotion])
                                        break
                newlog[0].append("State emotion")                            # add the title (Emotion) to the first row
                nextEmo = frstalog.next()                               # and change to the first significant emotion
                for logrow in newlog[1:]:                               # for all rows in the current log
                        if logrow[0] == nextEmo[0]:                     # when the timestep of the next emotion is found
                                latestEmo = nextEmo[1]                  # change the current emotion,
                                try:
                                    nextEmo = frstalog.next()           # and check what the next one to set up will be
                                except StopIteration:                    # unless we have reached the end of the FR state logfile (marked with END)
                                    nextEmo = "OVER"                    # because then we need to use a fake emotion that won't be found
                        logrow.append(latestEmo)                        # add the current emotion according to FR
#        print "STEP 2"
#        print newlog[0]
#        print newlog[1]
    
        ###
        ### STEP 3: add the secondary emotions that are above a certain threshold
        ###
        i = 0
        for logrow in newlog[1:]:                                       # for each line except the title one
                i += 1
                tmp = []
                for emo in logrow[1:8]:                                 # keep a temporary copy of the emotion values
                        try:
                                tmp.append(float(emo))                  # convert the string to float
                        except ValueError:                              # if it wasn't a float (i.e. a FIT_FAILED)
                                tmp.append(-2)                          # replace by -2, not to disturb the "max" after                
                while True:
                        x = max(tmp)                                    # get the most significant emotion
                        if x < self.secEmotLimit:                            # if it's below the threshold, stop here
                                break
                        try:
                            logrow.append(newlog[0][tmp.index(x)+1])        # otherwise, append the emotion name on the row (+1 as we deleted the first column here)
                        except IndexError:
                            print "line " + str(i)
                            print x
                            print logrow
                            sys.exit(1)
                        tmp[tmp.index(x)] = -1                          # and put that emotion value to -1
                        #print tmp
        
        newlog[0].extend(["1st emotion by score", "2nd emotion", "3rd emotion", "4th emotion", "5th emotion", "6th emotion", "7th emotion"])    # add the column title
        for logrow in newlog[1:]:                                       # make sure to have the right number of columns everywhere
            while len(logrow)!=len(newlog[0]):
                    logrow.append("")
#        print "STEP 3"
#        print newlog[0]
#        print newlog[1]

        ###
        ### STEP 4 (6 in MTEmoLA): detecting "significant" emotions (in the Noldus' meaning, i.e. if the emotion is there for 0.5s)
        ###
        if computeCustomEmotions:
            cptemo = [0,0,0,0,0,0,0]                                                # initialize a counter for each of the 7 emotions of FR
            cptemoabs = [0,0,0,0,0,0,0]                                           # initialize a counter for how many times the 7 emotions in FR have been undetected
            emoSigRaw = []
            agreementEmotions = [0,0,0,0,0,0]    # counter of agreement between calculated emotions and the FaceReader state
            nbTotEmoLines = 0
            
            with open("..\\Agreement.csv", 'a') as fAgg:        # file to save agreement values
                for logrow in newlog[2:]:                                               # for each line of the log
                    emoSigRaw.append([0,0,0,0,0,0,0])                        # for the moment, consider no emotion is significant
                    for i, emo in enumerate(logrow[1:8]):                                         # for each emotion, check if it's above the threshold of significance
                        if (emo != "FIT_FAILED" and emo != "FIND_FAILED"):
                            if float(emo) >= self.secEmotLimit:
                                cptemoabs[i] = 0                        # reset the missing emotion counter
                                cptemo[i] += 1                          # increment its related counter
                            else:
                                cptemoabs[i] += 1                       # increment the counter of missing emotion if it's below threshold
                        else:                                                   
                            cptemoabs[i] += 1                               # also increment the counter of missing emotion when there is an acquisition issue in FR
                        if cptemoabs[i] >= emoDisapPersistence:                 # if that emotion has been missing long enough
                            cptemo[i] = 0                                   # reset its counter of successive appearances
                        
                        if cptemo[i] >= emoAppPersistence:            # if the emotion is significant (has become or remained as such)
                            if (emo != "FIT_FAILED" and emo != "FIND_FAILED"):
                                emoSigRaw[-1][i] = float(emo)            # retrieve the score if the emotion is significant (it is not necessarily above .3 - it is necessarily above .3 only at the moment when the emotion becomes significant)
                            else:                
                                emoSigRaw[-1][i] = emoSigRaw[-2][i]    # when there is a FIT_FAILED, the previous value of the emotion is kept as the current one. So the emotion is still considered as significant.
                    #print "EMO: " +str(cptemo)
                    #print "ABS: " +str(cptemoabs)
                    # now record significant emotions in new column, in the same order as in columns 11 to 17
                        
                    logrow.extend(["","","","","","","", "","","","","","",""])    # add the 14 extra column for the custom significant emotions calculated below
                    
            
                newlog[0].extend(["1st instant sig. emo", "2nd instant sig. emo", "3rd instant sig. emo", "4th instant sig. emo", "5th instant sig. emo", "6th instant sig. emo", "7th instant sig. emo"])   # add the column titles
                newlog[0].extend(["1st duration sig. emo", "2nd duration sig. emo", "3rd duration sig. emo", "4th duration sig. emo", "5th duration sig. emo", "6th duration sig. emo", "7th duration sig. emo"])   # add the column titles
    #            print "STEP 4"
    #            print newlog[0]
    #            print newlog[1]
                self.initColumnIndexes(newlog[0])    # update the column indexes
                
                emoOrdInstant = []
                emoOrdDurat = []
                for iemo, emoTab in enumerate(emoSigRaw):
                    #if iemo%100 == 0:
                    #    print "line " + str(iemo)
                    emoOrdInstant.append([0,0,0,0,0,0,0])
                    emoOrdDurat.append([0,0,0,0,0,0,0])
                    # Get a sorted list of indexes of significant emotions (in this given row), where the first element is the most significant emotion
                    emoTabOrd = []
                    for i,j in enumerate(emoTab):
                        emoTabOrd.append([j, i])
                    # emoTabOrd: [[scoreNeu, 0], [scoreHap, 1], ..., [scoreDis, 6]]
                    emoTabOrd.sort()
                    emoTabOrd.reverse()        
                    # emoTabOrd: [[scoreEmoHighest, correspondingEmoId], [scoreEmoSecondHighest, correspondingEmoId], ..., [scoreEmoLowest, correspondingEmoId]]
                    #print "TABORD: " + str(emoTabOrd)
                    #emoTabOrd = map(lambda x:x[1], emoTabOrd)
                    # Insert a list where the most significant emotion (according to its position in the usual 7 elements vector of emotions) is given a value of 1, the second most significant a value of 2, etc. and the non-significant emotions remain with a value of 0
                    for i,e in enumerate(emoTabOrd):
                        if e[0] >= self.secEmotLimit:
                            emoOrdInstant[-1][e[1]] = i+1
                        else:
                            emoOrdInstant[-1][e[1]] = 0
                    #print "ORDINS: " + str(emoOrdInstant[-1])
                    
                    if (iemo >= emoAppPersistence):        # not to have any value for the first 0.5s
                        firstError = True
                        for i in range(0,7):
                            try:
                                # Look for the index of the first significant emotion, the second, the third, etc.
                                idx = emoOrdInstant[-1].index(i+1)
                                # the INSTANTANEOUS primaries significant emotions
                                newlog[iemo+2][-14+i] = newlog[1][idx+1]
                            except ValueError:
                                if (i == 0 or firstError):    # the first column, or the first column without any emotion name in it, should contain "Unknown", in order to calculate agreement with the state column of FaceReader
                                    newlog[iemo+2][-14+i] = "Unknown"
                                else:
                                    newlog[iemo+2][-14+i] = ""
                                firstError = False
                    else:    # for the first lines, we want to display one unknown first
                        for i in range(0,7):
                            if i == 0:
                                newlog[iemo+2][-14+i] = "Unknown"
                            else:
                                newlog[iemo+2][-14+i] = ""
                    
                    # Now compute the most significant lasting emotion, a la FaceReader, which considers that when 2 emotions A and B are significant, if emotion A was primary (and with a higher score) and B secondary (and with a lower score than A), then when B starts having a higher score than A (with both being significant all along), it will only be considered as the new primary emotion after a threshold of again 0.5s
                    sumEmo = [[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]]
                    # sumEmo is a matrix containing for each emotion, the number of time it has been 1st, 2nd, ... 7th significant emotion, over the last second
            #        if (iemo >= emoDisapPersistence):        # it's fine anyhow
                    for el in emoOrdInstant[-1*emoDisapPersistence:]:
                        for ei, e in enumerate(el):
                            if e != 0:    # when the emotion was significant, count it, otherwise, just ignore
                                sumEmo[ei][e-1] += 1
                    
                    #print sumEmo
                    emoTabOrd = []
                    for i,j in enumerate(sumEmo):
                        emoTabOrd.append([j, i])
                    # emoTabOrd = [[[#times Neutral was 1st the last second, #times Neutral was 2nd the last second, ..., #times Neutral was 7th the last second], 0], ..., [[#times Disgusted was 1st the last second, ...], 7]]
                    emoTabOrd.sort()
                    emoTabOrd.reverse()
                    # emoTabOrd = [[[#times emotion 1st the most often was 1st the last second, #times emotion 1st the most often was 2nd the last second, ...], index of emotion 1st the most often the last second], ...]
                    #print "TABPRO:" + str(emoTabOrd)
                    emoTabOrd = map(lambda x:(x[1] if x[0] != [0,0,0,0,0,0,0] else -1), emoTabOrd)
                    # emoTabOrd = [index of the most frequent emotion the past second, ..., -1, -1], indexes replaced by -1 if no significance past second
                    removeNonSigEmo = True
                    for e in emoTabOrd:
                        while removeNonSigEmo:
                            try:
                                emoTabOrd.remove(-1)
                            except ValueError:
                                removeNonSigEmo = False
                    # emoTabOrd = only indexes of emotions with some significance (-1 cleaned out)
                    
                    #sleep(1)
            #        print "TABORD:" + str(emoTabOrd)        
                    # all the emotions are there, but we want to display only those that are significant right now (we currently have index of the most significant emotion over the period, then the 2nd most significant over the period, etc.)
                    for i,e in enumerate(emoTabOrd):
                        emoOrdDurat[-1][e] = i+1
            #            if emoOrdInstant[-1][i] != 0:    # if the emotion is currently significant, take its rank
            #                emoOrdDurat[-1][i] = emoTabOrd[i]   # temporarily keep all the emotions    
            #        print emoOrdDurat[-1]
            #        sleep(0.25)
                    if (iemo >= emoAppPersistence):        # not to have any value for the first 0.5s
                        firstError = True
                        for i in range(0,7):
                            try:
                                # Look for the index of the first significant emotion, the second, the third, etc.
                                idx = emoOrdDurat[-1].index(i+1)
                                # the primaries significant emotions OVER TIME
                                newlog[iemo+2][-7+i] = newlog[1][idx+1]
                
                            except ValueError:
                                if (i == 0 or firstError):    # the first column, or the first column without any emotion name in it, should contain "Unknown", in order to calculate agreement with the state column of FaceReader
                                    newlog[iemo+2][-7+i] = "Unknown"
                                else:
                                    newlog[iemo+2][-7+i] = ""
                                firstError = False
                    else:    # for the first lines, we want to display one unknown first
                        for i in range(0,7):
                            if i == 0:
                                newlog[iemo+2][-7+i] = "Unknown"
                            else:
                                newlog[iemo+2][-7+i] = ""
                    
                    # check agreement
                    if (newlog[iemo+2][self.dictColIdx["State emotion"]] == newlog[iemo+2][self.dictColIdx["1st emotion by score"]]):
                        agreementEmotions[0] += 1
                    if (newlog[iemo+2][self.dictColIdx["State emotion"]] in newlog[iemo+2][self.dictColIdx["1st emotion by score"]:self.dictColIdx["1st emotion by score"]+7]):    # check agreement
                        agreementEmotions[1] += 1
                    if (newlog[iemo+2][self.dictColIdx["State emotion"]] == newlog[iemo+2][self.dictColIdx["1st instant sig. emo"]]):
                        agreementEmotions[2] += 1
                    if (newlog[iemo+2][self.dictColIdx["State emotion"]] in newlog[iemo+2][self.dictColIdx["1st instant sig. emo"]:self.dictColIdx["1st instant sig. emo"]+7]):    # check agreement
                        agreementEmotions[3] += 1
                    if (newlog[iemo+2][self.dictColIdx["State emotion"]] == newlog[iemo+2][self.dictColIdx["1st duration sig. emo"]]):
                        agreementEmotions[4] += 1        
                    if (newlog[iemo+2][self.dictColIdx["State emotion"]] in newlog[iemo+2][self.dictColIdx["1st duration sig. emo"]:self.dictColIdx["1st duration sig. emo"]+7]):    # check agreement
                        agreementEmotions[5] += 1
                    nbTotEmoLines += 1
            
                print "Agreement [FR state] / [score-only primary emotion]: " + str(100*float(agreementEmotions[0])/nbTotEmoLines)[:5] + "%"
                print "Agreement [FR state] / [all score-only emotions]: " + str(100*float(agreementEmotions[1])/nbTotEmoLines)[:5] + "%"
                print "Agreement [FR state] / [instant primary emotion]: " + str(100*float(agreementEmotions[2])/nbTotEmoLines)[:5] + "%"
                print "Agreement [FR state] / [all instant emotions]: " + str(100*float(agreementEmotions[3])/nbTotEmoLines)[:5] + "%"
                print "Agreement [FR state] / [duration primary emotion]: " + str(100*float(agreementEmotions[4])/nbTotEmoLines)[:5] + "%"
                print "Agreement [FR state] / [all duration emotions]: " + str(100*float(agreementEmotions[5])/nbTotEmoLines)[:5] + "%"
                
                writer = csv.writer(fAgg, dialect=csv.excel)
                wrow = [subject.ID]
                wrow.extend(map(lambda(x): str(100*float(x)/nbTotEmoLines), agreementEmotions))
                #writer.writerow([cleanID, str(100*float(agreementEmotions[0])/nbTotEmoLines), str(100*float(agreementEmotions[1])/nbTotEmoLines), str(100*float(agreementEmotions[2])/nbTotEmoLines), str(100*float(agreementEmotions[3])/nbTotEmoLines), str(100*float(agreementEmotions[4])/nbTotEmoLines), str(100*float(agreementEmotions[5])/nbTotEmoLines)])
                writer.writerow(wrow)
        
        subject.log = newlog
    