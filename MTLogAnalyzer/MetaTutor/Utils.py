'''
Created on 2012-10-12

@author: Francois
'''

import csv

class Utils(object):
    '''
    Class used to group various util functions, mostly ndependent from each other
    '''

    @staticmethod
    def cleanbr(s):
        """Delete the trailing \r or \n at the end of a line"""
        if s.endswith('\r\n'):
            return s[:-2]
        elif s.endswith('\r') or s.endswith('\n'):
            return s[:-1]
        else:
            return s

    @staticmethod
    def transpose(tab):
        """Transpose a matrix"""
        # return ([ a for a,b in tab ], [ b for a,b in tab ])
        return zip(*tab)

    @staticmethod
    def getLastElementOfClass(l, c):
        """Retrieve from a list of objects the last one (i.e. the first one from the end) that is an instance of the class given as parameter"""
        l.reverse()
        val = (i for i in l if isinstance(i, c)).next()
        l.reverse()
        return val

    @staticmethod
    def getSecondsFromDatetime(dt):
        return (dt.hour * 3600 + dt.minute * 60 + dt.second)
    
    @staticmethod
    def getMilliSecondsFromDatetime(dt):
        #added by bondaria
        return (dt.hour * 3600 + dt.minute * 60 + dt.second) * 1000 + dt.microsecond / 1000
    
    @staticmethod
    def exportString2Excel(content, expfile="out.csv"):
        """Export a content given as a string where columns are separated by \t and rows by \n, 
        to a comma separated value file to be imported into Excel"""
        l = content.split("\n")
        l2 = []
        for e in l[:-1]:    # drop the last empty element
            l2.append(e.split("\t"))
        Utils.exportList2Excel(l2, expfile)
            
    @staticmethod
    def exportList2Excel(l, expfile="out.csv"):
        """Export a 2-level list (e.g. [[a,b,c],[d,e,f], ...]) such as each level 1 element represents a row 
        and each level 2 element represents a cell of the row, 
        to a comma separated value file to be imported into Excel"""
        with open(expfile, 'wb') as f:     # always open CSV files in binary for Windows, otherwise introduce a blank line
            writer = csv.writer(f, dialect='excel')
            for row in l:
                #print row
                writer.writerow(row)