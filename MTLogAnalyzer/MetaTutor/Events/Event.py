"""
Created on 14 mars 2011

@author: F. Bouchet (francois.bouchet@mcgill.ca)
"""

import datetime

class Event(object):
    """A basic event, either from a log or extracted from an analysis"""
    
    subStyles = {"Browse":['<font color="#ff0000">', '</font>'],
                 "Notes":['<font color="#0000ff">', '</font>'],
                 "Quiz":['<font color="#339900">', '</font>'],
                 "UserActivity":['<i>', '</i>']}
    """Dictionary of named visual styles to be used by subtitles for events.
    Values correspond to a list of two elements: the opening tag and the closing tag."""
    
    def __init__(self, logger, style):
        #self.logger = logger    # saving the logger prevents pickling from working
        """logging system to display messages"""
        if style in self.subStyles.keys():
            self.styleStart = self.subStyles[style][0]
            """Opening tag of the style to apply to the content of an event when displaying it as a subtitle"""
            self.styleEnd = self.subStyles[style][1]
            """Closing tag of the style to apply to the content of an event when displaying it as a subtitle"""
        else:
            self.styleStart = ""
            self.styleEnd = ""
    
    def getInfo(self, showAll=False):
        return [str(type(self)).split(".")[-1].split("'")[0]]
        
    @staticmethod
    def convertTimeMT2Standard(timestamp):
        """Convert a timestamp from the MetaTutor log to a standard datetime.datetime object with the HH:MM:SS.mmm format"""
        timest = int(timestamp)
        #return datetime.time(timest/3600000, (timest/60000)%60, (timest/1000)%60, (timest%1000)*1000)
        return datetime.datetime(1900, 1, 1, timest/3600000, (timest/60000)%60, (timest/1000)%60, (timest%1000)*1000)

    @staticmethod
    def convertAbsTimeMT2Standard(timestamp):
        """Convert the absolute time from the MetaTutor log (HH:MM:SS) to a datetime.datetime object"""
        ts = timestamp.split(":")
        offset = 0
        end = ts[2].split(" ")  # deal with events with a different format (with AM/PM), for the notepad
        if len(end) > 1:
            ts[2] = end[0]
            if (end[1] == "PM" and ts[0] != "12"):    # for events with a PM at the end, increase the hour of 12
                offset = 12
        return datetime.datetime(1900, 1, 1, int(ts[0]) + offset, int(ts[1]), int(ts[2]), 0)

    @staticmethod
    def convertTimeStandard2String(timestamp):
        """Convert a datetime.datetime object to a string with format "HH:MM:SS.mmm" and returns it"""
        return timestamp.time().strftime("%H:%M:%S.%f")[:12]
    
    @staticmethod
    def convertTimeDelta2String(timed):
        """Convert a datetime.timedelta object to a string with format "HH:MM:SS.mmm" and returns it"""
        return str(timed.seconds/3600).zfill(2) + ":" + str((timed.seconds/60)%60).zfill(2) + ":" + str(timed.seconds%60).zfill(2) + "." + str(timed.microseconds)[:3].zfill(3)
    
    @staticmethod
    def convertString2TimeDelta(stime):
        """Convert a string with format "HH:MM:SS.mmm" to a datetime.timedelta object and returns it"""
        try:
            res = datetime.timedelta(seconds=int(stime[0:2])*3600+int(stime[3:5])*60+int(stime[6:8]), microseconds=int(stime[9:12])*1000)
            return res
        except ValueError:
            print "Problem with time string: " + str(stime)
            raise ValueError

class MTEvent(Event):
    """An event from MetaTutor log"""
    def __init__(self, logger, eventID, eventType, absolutetime, timestamp, style=""):
        Event.__init__(self, logger, style)
        self.eventID = eventID
        """A unique ID to identify the event during a MT session"""
        self.eventType = eventType
        """Type of the event (from 0 to 8 - corresponding to the 4th column in the logs)"""
        if isinstance(absolutetime, datetime.datetime):
            self.absoluteTime = absolutetime
        else:
            self.absoluteTime = self.convertAbsTimeMT2Standard(absolutetime)
        """Datetime.datetime object which time parameters correspond to the absolute time of the system (date is 1900/01/01)"""
        if isinstance(timestamp, datetime.datetime):
            self.timestamp = timestamp
        else:
            self.timestamp = self.convertTimeMT2Standard(timestamp)
        """Datetime.datetime object representing the timestamp of an event using the MT referential of time"""
        self.sub = ""
        """Subtitle associated to this event"""
        self.emotionValence = 0
        """valence of the emotion attached to this event, calculated a posteriori by independent function that could be based on various data channels (e.g., FaceReader)"""
    
    def getInfo(self, showAll=False):
        l = Event.getInfo(self, showAll)
        l.extend([self.convertTimeStandard2String(self.absoluteTime), self.convertTimeStandard2String(self.timestamp), "(punctual)"])
        return l
    
    def getTimeStart(self):
        return self.timestamp
    def getTimeEnd(self):
        return self.timestamp

    
class MTUnknownEventException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
