#Script to compare the offline and online fixations detected by the fixation detectors of the Experiment platform
#@Sebastien Lalle

import csv
import numpy as np
import os
import pandas as pd
import math

def fixation_detection(x, y, time, maxdist=35, mindur=100, smi=False):
        """
        This the the detector itnegrated in the platform!

        Detects fixations, defined as consecutive samples with an inter-sample
        distance of less than a set amount of pixels (disregarding missing data)

        arguments
        x        -    numpy array of x positions
        y        -    numpy array of y positions
        time        -    numpy array of timestamps

        keyword arguments
        maxdist    -    maximal inter sample distance in pixels (default = 35)
        mindur    -    minimal duration of a fixation in milliseconds; detected
                    fixation candidates will be disregarded if they are below
                    this duration (default = 100)

        returns
        Sfix, Efix
                    Sfix    -    list of lists, each containing [starttime], for Start of Fixation
                    Efix    -    list of lists, each containing [starttime, endtime, duration, endx, endy], for End of Fixation
        """
        if smi:
            mindur = mindur*1000
        # empty list to contain data
        Sfix = []
        Efix = []
        # print(list(zip(x,y)))

        # loop through all coordinates
        si = 0
        fixstart = False
        #print "in fixation algorithm"
        #print x
        for i in range(1,len(x)):
            # calculate Euclidean distance from the current fixation coordinate
            # to the next coordinate
            dist = ((x[si]-x[i])**2 + (y[si]-y[i])**2)**0.5
            # check if the next coordinate is below maximal distance
            # print(fixstart)

            if dist <= maxdist and not fixstart:
                # start a new fixation
                si = 0 + i
                fixstart = True
                Sfix.append([time[i]])
                # print('Start',si,time[i])
            elif dist > maxdist and fixstart:
                # end the current fixation
                fixstart = False
                # only store the fixation if the duration is ok
                t = time[i-1]-Sfix[-1][0]
                # print(dist,maxdist)
                # print("coor",list(zip(x[si:i],y[si:i])))
                # print("END",i,time[i])
                # print("time",t)
                if  t>= mindur:
                    x_fix = np.median(x[si:i-1])
                    y_fix = np.median(y[si:i-1])
                    Efix.append([Sfix[-1][0], time[i-1], time[i-1]-Sfix[-1][0], x_fix, y_fix])
                # delete the last fixation start if it was too short
                else:
                    Sfix.pop(-1)
                si = 0 + i
            elif not fixstart:
                si += 1

        return Sfix, Efix

def get_saccade_distance(saccade_gaze_points):
    distance = 0.0
    try:
        for i in range(0, len(saccade_gaze_points)-1):
            (timestamp1, point1x, point1y) = saccade_gaze_points[i]
            (timestamp2, point2x, point2y) = saccade_gaze_points[i+1]
            distance += float(math.sqrt( float(math.pow(point1x - point2x, 2) + math.pow(point1y - point2y, 2)) ))
    except Exception as e:
        warn(str(e))

    return (distance)

def saccade_detection(x, y, time, missing=0.0, minlen=5, maxvel=40, maxacc=340,smi=False):
    """
    Currently NOT USED! But included here as for possible future tests of saccade detection (#TODO)

    Detects saccades, defined as consecutive samples with an inter-sample
    velocity of over a velocity threshold or an acceleration threshold

    arguments
    x        -    numpy array of x positions
    y        -    numpy array of y positions
    time        -    numpy array of tracker timestamps in milliseconds
    keyword arguments
    missing    -    value to be used for missing data (default = 0.0)
    minlen    -    minimal length of saccades in milliseconds; all detected
                saccades with len(sac) < minlen will be ignored
                (default = 5)
    maxvel    -    velocity threshold in pixels/second (default = 40)
    maxacc    -    acceleration threshold in pixels / second**2
                (default = 340)

    returns
    Ssac, Esac
            Ssac    -    list of lists, each containing [starttime]
            Esac    -    list of lists, each containing [starttime, endtime, duration, startx, starty, endx, endy]
    """

    # CONTAINERS
    Ssac = []
    Esac = []

    # INTER-SAMPLE MEASURES
    # the distance between samples is the square root of the sum
    # of the squared horizontal and vertical interdistances
    intdist = (np.diff(x)**2 + np.diff(y)**2)**0.5
    # get inter-sample times
    inttime = np.diff(time)
    # recalculate inter-sample times to seconds
    if smi:
        inttime = inttime / 1000000
    else:
        inttime = inttime / 1000.0

    # VELOCITY AND ACCELERATION
    # the velocity between samples is the inter-sample distance
    # divided by the inter-sample time
    vel = intdist / inttime
    # the acceleration is the sample-to-sample difference in
    # eye movement velocity
    acc = np.diff(vel)

    # SACCADE START AND END
    t0i = 0
    stop = False
    while not stop:
        # saccade start (t1) is when the velocity or acceleration
        # surpass threshold, saccade end (t2) is when both return
        # under threshold

        # detect saccade starts
        sacstarts = np.where((vel[1+t0i:] > maxvel).astype(int) + (acc[t0i:] > maxacc).astype(int) >= 1)[0]
        if len(sacstarts) > 0:
            # timestamp for starting position
            t1i = t0i + sacstarts[0] + 1
            if t1i >= len(time)-1:
                t1i = len(time)-2
            t1 = time[t1i]

            # add to saccade starts
            Ssac.append([t1])

            # detect saccade endings
            sacends = np.where((vel[1+t1i:] < maxvel).astype(int) + (acc[t1i:] < maxacc).astype(int) == 2)[0]
            if len(sacends) > 0:
                # timestamp for ending position
                t2i = sacends[0] + 1 + t1i + 2
                if t2i >= len(time):
                    t2i = len(time)-1
                t2 = time[t2i]
                dur = t2 - t1

                # ignore saccades that did not last long enough
                if dur >= minlen:
                    gazepoints=list(zip(time[t1i:t2i],x[t1i:t2i],y[t1i:t2i]))
                    # for i in range(t1i,t2i,1):
                    #     gazepoints.append((time[i],x[i],y[i]))
                    d = get_saccade_distance(gazepoints)
                    # add to saccade ends
                    Esac.append([t1, t2, dur, d, x[t1i], y[t1i], x[t2i], y[t2i]])
                else:
                    # remove last saccade start on too low duration
                    Ssac.pop(-1)

                # update t0i
                t0i = 0 + t2i
            else:
                stop = True
        else:
            stop = True

    return Esac
    # return Ssac, Esac


def read(filename):
    """
    Read the list of raw gaze samples.
    Current format is a tsv file with 3 columns: [timestamp, x, y]
    Timestamp is the time of the gaze sample in microseconds, x and y are its coordinates.
    Currently done by filtering the "EyeTrackerTimestamp",  "GazePointX (ADCSpx)",  and "GazePointY (ADCSpx)" fields from the Tobii Studio V3 output
    """
    with open(filename) as f:
        header = True
        gaze_x = []
        gaze_y = []
        timestamps = []


        for row in f:
            if header:
                header = False
                continue

            row_array = row.strip().split("\t")

            if (len(row_array) != 3): #ignore lines with incorrecty number of colums
                continue

            if row_array[0] == "" or row_array[1]  == "" or row_array[2]  == "": #ignore gaze samples with missing info
                continue

            temptime = int(round(float(row_array[0])/1000.0, 0)) #convert unit from microseconds to milliseconds [#TODO change as needed depending on data input]

            x = int(row_array[1])
            y = int(row_array[2])
            gaze_x.append(x)
            gaze_y.append(y)
            timestamps.append(temptime)

        return timestamps, gaze_x, gaze_y


def offlinefix(x, y, time, smi=False):
    """
    Simply run the algorithm offline, i.e., on the entire list of gaze samples
    Returns a list of Efix (end fixation information, see fixation_detection() above
    """
    EndFixations = []
    Sfix, Efix = fixation_detection(x, y, time, smi=smi)
    for fix in Efix:
       EndFixations.append([fix])
    return EndFixations


def simulrealtimefix(x, y, time):
    """
    Simulate the real time detection of the fixations as done in the experimenter platforms,
    by reading and processing previously recorded gaze sample one at a time, as it is done in real time.
    Returns a list of Efix (end fixation information, see fixation_detection() above
    """
    EndFixations = []
    array_index = 0
    array_iterator = 7

    newX = []
    newY = []
    newTime = []

    while(1):
        print ("Realtime fixation - in outter loop")
        curX = x[array_index:(array_index + array_iterator)]
        curY = y[array_index:(array_index + array_iterator)]
        curTime = time[array_index:(array_index + array_iterator)]

        newX = curX
        newY = curY
        newTime = curTime

        if(curX == []):
            break

        [Sfix, Efix] = fixation_detection(curX, curY, curTime)
        #print "after calling fixation_detection in outter loop"
        #print Sfix
        #print Efix
        #When there is no fixation detected yet
        while(1):
            #print "in inner loop"
            if(Sfix == []):
                #print "in inner loop if statement"
                array_index = array_index + array_iterator
                nextX = x[array_index:(array_index + array_iterator)]
                nextY = y[array_index:(array_index + array_iterator)]
                nextTime = time[array_index:(array_index + array_iterator)]

                """print "newX in 1st while loop"
                print newX
                print "nextX in 1st while loop:"
                print nextX

                print "curX in 1st while loop:"
                print curX
                """

                newX = curX + nextX
                #print "newX after extending in 1st while loop"
                #print newX
                newY = curY + nextY
                newTime = curTime + nextTime
                #print "calling method in first inner loop"
                [Sfix, Efix] = fixation_detection(newX, newY, newTime)
                #print "after calling in first inner loop"

                curX = nextX
                curY = nextY
                curTime = nextTime
            else:
                break
            if(nextX == []):
                break

        #When fixation is detected
        while(1):
            print("New fixation detected")
            if(Efix == []):
                #print "in second inner while loop if statement"
                array_index = array_index + array_iterator
                nextX = x[array_index:(array_index + array_iterator)]
                nextY = y[array_index:(array_index + array_iterator)]
                nextTime = time[array_index:(array_index + array_iterator)]

                #print "newX in 2nd while loop:"
                #print newX
                #print "nextX in 2nd while loop:"
                #print nextX

                #newX should extend itself
                #newX = newX.extend(nextX)
                newX.extend(nextX)
                #print "*******newX after extending in 2nd while loop*******"
                #print newX
                newY.extend(nextY)
                newTime.extend(nextTime)

                #print "calling method in first inner loop"
                [Sfix, Efix] = fixation_detection(newX, newY, newTime)
                #print "after calling in first inner loop"
                #print Sfix
                #print Efix
            else:
                EndFixations.append(Efix)


                EfixEndTime = Efix[0][1]
                '''
                print "printing newTime"
                print newTime
                print "printing size of newTime"
                print len(newTime)
                print "printing EfixEndTime"
                print EfixEndTime
                print "printing next time"
                print nextTime
                print "printing array_index"
                print array_index
                print "printing index of newTime"
                print newTime.index(EfixEndTime)
                #endTimeIndex = nextTime.index(EfixEndTime)
                #array_index = array_index + endTimeIndex
                '''
                array_index = time.index(EfixEndTime) + 1

                #print EndFixations

                #print a
                #array_index = array_index + array_iterator
                print("appending EndFixations")
                break
            if(nextX == []):
                break

    return EndFixations



############################################################################ MAIN ##
# if __name__ == "__main__":
#     [time, x, y] = read('P18copy.tsv') #read the historical fixations
#
#     #detect fixations
#     myfixations_real =  simulrealtimefix(x,y,time) ##simulated real time
#     myfixations_off =  offlinefix(x,y,time) ##fully offline
#
#     #writing output
#     outputfile_real = 'myfixations_P18_realtime.csv'
#     outputfile_off = 'myfixations_P18_offline.csv'
#
#     print "\nWriting output in "+str(outputfile_real)+" and "+str(outputfile_off)+"\n"
#     fl = open(outputfile_real, 'wb')
#     writer = csv.writer(fl)
#     writer.writerow(['fix_start_time', 'fix_end_time', 'fix_duration', 'fix_x', 'fix_y'])
#     for values in myfixations_real:
#         #print values
#         writer.writerow(values[0])
#     fl.close()
#
#     fl = open(outputfile_off, 'wb')
#     writer = csv.writer(fl)
#     writer.writerow(['fix_start_time', 'fix_end_time', 'fix_duration', 'fix_x', 'fix_y'])
#     for values in myfixations_off:
#         #print values
#         writer.writerow(values[0])
#     fl.close()


eye_path='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/EyeTrackingData'

date=dict()
eye_start=dict()
for file in os.listdir(eye_path):
    if 'All-Data' in file and file.split('.')[-1] =='tsv':
        id = file.split('-')[0].upper()
        with open(os.path.join(eye_path,file),'r') as f:
            df = pd.read_csv(f, sep='\t',skiprows=23)#skip to the data
            df = df.loc[:,['Timestamp','GazePointX','GazePointY']].dropna()
            time = list(df['Timestamp'])
            x = list(df['GazePointX'])
            y = list(df['GazePointY'])

            # print(x.count(0)/len(x))
            # print(x)
            myfixations_off =  offlinefix(x,y,time) ##fully offline
            # print(myfixations_off)
            # mysaccades_off =  saccade_detection(x,y,time) ##fully offline
            outputfile_off = '/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/EyeTrackingData/Fixations/' + id +'-Fixations.csv'
            sacfile_off = '/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/EyeTrackingData/Saccades/' + id +'-Saccades.csv'


            fl = open(outputfile_off, 'w')
            writer = csv.writer(fl)
            writer.writerow(['index','fix_start_time', 'fix_end_time', 'fix_duration', 'fix_x', 'fix_y'])
            i = 0
            for values in myfixations_off:
                # print(values)
                values[0].insert(0,i)
                writer.writerow(values[0])
                i+=1
            fl.close()

            # fl = open(sacfile_off, 'w')
            # writer = csv.writer(fl)
            # writer.writerow(['index','sac_start_time', 'sac_end_time', 'sac_duration', 'sac_distance', 'sac_start_x', 'sac_start_y', 'sac_end_x', 'sac_end_y'])
            # i = 0
            # for values in mysaccades_off:
            #     # print(values)
            #     values.insert(0,i)
            #     writer.writerow(values)
            #     i+=1
            # fl.close()


eye_path='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2016/Eye Tracking Data/SMI Data/Corrected'

date=dict()
eye_start=dict()
for file in os.listdir(eye_path):
    if 'Raw' in file and file.split('.')[-1] =='csv':
        id = file.split('-')[0].upper()
        with open(os.path.join(eye_path,file),'r') as f:
            df = pd.read_csv(f, sep=',',skiprows=37)#skip to the data
            df = df.loc[:,['Time','L POR X [px]','L POR Y [px]', 'R POR X [px]', 'R POR Y [px]']].dropna()
            time = list(df['Time'])
            x = list((df['L POR X [px]'] + df['R POR X [px]'])/2)
            y = list((df['L POR Y [px]'] + df['R POR Y [px]'])/2)
            myfixations_off =  offlinefix(x,y,time,smi=True) ##fully offline
            # mysaccades_off =  saccade_detection(x,y,time,smi=True) ##fully offline
            outputfile_off = '/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2016/Eye Tracking Data/SMI Data/Fixations/' + id +'-Fixations.csv'
            sacfile_off = '/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2016/Eye Tracking Data/SMI Data/Saccades/' + id +'-Saccades.csv'


            fl = open(outputfile_off, 'w')
            writer = csv.writer(fl)
            writer.writerow(['index','fix_start_time', 'fix_end_time', 'fix_duration', 'fix_x', 'fix_y'])
            i = 0
            for values in myfixations_off:
                # print(values)
                values[0].insert(0,i)
                writer.writerow(values[0])
                i+=1
            fl.close()
#
#
#             fl = open(sacfile_off, 'w')
#             writer = csv.writer(fl)
#             writer.writerow(['index','sac_start_time', 'sac_end_time', 'sac_duration', 'sac_distance', 'sac_start_x', 'sac_start_y', 'sac_end_x', 'sac_end_y'])
#             i = 0
#             for values in mysaccades_off:
#                 # print(values)
#                 values.insert(0,i)
#                 writer.writerow(values)
#                 i+=1
#             fl.close()
