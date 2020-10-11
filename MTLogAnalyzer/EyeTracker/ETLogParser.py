'''
Created on 2012-10-15

@author: Francois
'''

import csv
import datetime
from collections import namedtuple
from recordtype import  *  # for recordtype elements, which are mutable version of namedtuples

class ETLogParser(object):
    '''
    classdocs
    '''
    AoiFixation = recordtype("AoiFixation", "timeStart, timeEnd, nbFixations, aoiName") # merge a sequence of consecutive fixations to the same AOI into a 4-tuple

    def __init__(self):
        '''
        Constructor
        '''
    
    @staticmethod
    def parseAOILog(participantID):
        path = "C:/Users/Francois/workspace/ETMTAOIExtractor/src/Output-splitted"
        filename = "filteredAOIs-MT208PN" + participantID + ".tsv"
        #filepatt = re.compile("filteredAOIs-MT208PN[0-9]+.tsv")
#        dictAoiTime = {}
        aoiFixationsList = []
        
        
        #for file in os.listdir(path):
        #    if os.path.isfile(os.path.join(path, file)) and filepatt.match(file) != None:
        with open(path + "/" + filename, 'r') as fin:
            etlog = csv.reader(fin, dialect="excel", delimiter="\t")
            queuedAois = {}
            prevAois = []
            for row in etlog:
                rowAoisList = eval(row[1])  # get all the AOIs associated to the current timestamp
                try:
                    rowTime = datetime.datetime.strptime(row[0], "%H:%M:%S.%f")
                except ValueError:
                    rowTime = datetime.datetime.strptime(row[0], "%H:%M:%S")    # for lines that do not have microseconds provided
                for aoi in rowAoisList:
                    # addition to the dictionary
#                    if aoi in dictAoiTime.keys():
#                        dictAoiTime[aoi].append(rowTime)
#                    else:
#                        dictAoiTime[aoi] = [rowTime]
                    
                    # addition to the list
                    if aoi in prevAois:
                        queuedAois[aoi].timeEnd = rowTime   # update the end time
                        queuedAois[aoi].nbFixations += 1        # increment the number of fixations
                    else:
                        queuedAois[aoi] = ETLogParser.AoiFixation(rowTime, rowTime, 1, aoi) # add the current row to the queue
                
                aoiToDelete = []
                for aoi in queuedAois:  # unqueue AOIs that are not longer in the current row
                    if aoi not in rowAoisList:
                        aoiFixationsList.append(queuedAois[aoi])
                        aoiToDelete.append(aoi) # mark the aoi as to be deleted (can't delete during iteration)
                for aoi in aoiToDelete:
                    del(queuedAois[aoi])
                        
                prevAois = rowAoisList  # update the list of previous AOIs
        
        #print aoiFixationsList
        return aoiFixationsList