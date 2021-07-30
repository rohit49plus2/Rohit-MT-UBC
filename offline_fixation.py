#Script to compare the offline and online fixations detected by the fixation detectors of the Experiment platform
#@Sebastien Lalle

import csv
import numpy as np
import os
import pandas as pd
import math
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from sklearn.linear_model import LinearRegression

# N = 5

def stats(id,x, y, time,smi=False):
    """
    Currently NOT USED! But included here as for possible future tests of saccade detection (#TODO)

    Detects saccades, defined as consecutive samples with an inter-sample
    velocity of over a velocity threshold or an acceleration threshold

    arguments
    x        -    numpy array of x positions
    y        -    numpy array of y positions
    time     -    numpy array of tracker timestamps in milliseconds
    """


    # INTER-SAMPLE MEASURES
    # the distance between samples is the square root of the sum
    # of the squared horizontal and vertical interdistances
    intdist = (np.diff(x)**2 + np.diff(y)**2)**0.5
    # get inter-sample times
    inttime = np.diff(time)
    # recalculate inter-sample times to seconds
    if smi:
        inttime = inttime / 1000000.0
    else:
        inttime = inttime / 1000.0


    # VELOCITY AND ACCELERATION
    # the velocity between samples is the inter-sample distance
    # divided by the inter-sample time
    vel = intdist / inttime
    # print(vel.shape)
    # print(intdist.shape)
    # print(inttime.shape)
    # the acceleration is the sample-to-sample difference in
    # eye movement velocity
    vel_dif=np.diff(vel)
    # print(vel_dif.shape)
    # vel_dif = np.insert(vel_dif,0,0)
    acc = np.divide(vel_dif,np.delete(inttime,0))

    print('id',id)
    # print("intdist")
    # print(np.mean(intdist))
    # print(np.std(intdist))
    # print(np.max(intdist))
    # print(np.min(intdist))
    # print("vel")
    # print(np.mean(vel))
    # print(np.std(vel))
    # print(np.max(vel))
    # print(np.min(vel))
    # print("acc")
    # print(np.mean(acc))
    # print(np.std(acc))
    # print(np.max(acc))
    # print(np.min(acc))

    dt = 0.016
    t = np.arange(0, 20, dt)

    if smi:
        study = '2016'
    else:
        study = '2014'

    # plt.rc('font', size=20) #controls default text size
    # plt.rc('axes', titlesize=20) #fontsize of the title
    # plt.rc('axes', labelsize=12) #fontsize of the x and y labels
    # plt.rc('xtick', labelsize=8) #fontsize of the x tick labels
    # plt.rc('ytick', labelsize=8) #fontsize of the y tick labels

    fig, axs = plt.subplots(2, 1)
    fig.suptitle(study+' participant',fontsize=24)
    axs[0].plot(t, vel[:len(t)])
    # axs[0].set_xlim(0, 2)
    axs[0].set_xlabel('time')
    axs[0].set_ylabel('velocity in pixels/second')
    axs[0].set_title('Velocity')
    axs[0].grid(True)

    axs[1].plot(t,acc[:len(t)])
    axs[1].set_xlabel('time')
    axs[1].set_ylabel('acceleration in pixels/second^2')
    axs[1].set_title('Acceleration')
    axs[1].grid(True)

    fig.tight_layout()
    plt.show()


    return

def fixation_detection(x, y, time, maxdist=35, mindur=100, smi=False,N=5):
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
        missing = False
        for i in range(1,len(x)):
            # calculate Euclidean distance from the current fixation coordinate
            # to the next coordinate
            if (x[i]==0.0) & (y[i] ==0.0) and i>N:
                missing=True
            else:
                missing=False

            if missing:
                gaze = np.array(list(zip(x[i-N:i],y[i-N:i])))
                # print(gaze.shape)
                times = np.array(time[i-N:i]).reshape(-1,1)
                # print(times.shape)
                # print(times)
                # print(gaze)
                lr = LinearRegression().fit(times,gaze)
                x[i]=lr.predict([[time[i]]])[0][0]
                y[i]=lr.predict([[time[i]]])[0][1]

            # print(list(zip(x,y)))



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
                # print("time",t,mindur)
                if  t>= mindur:
                    # print("appending")
                    x_fix = np.median(x[si:i-1])
                    y_fix = np.median(y[si:i-1])
                    Efix.append([Sfix[-1][0], time[i-1], time[i-1]-Sfix[-1][0], x_fix, y_fix])
                # delete the last fixation start if it was too short
                else:
                    Sfix.pop(-1)
                si = 0 + i
            elif not fixstart:
                si += 1

            # print(Efix)

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

def saccade_detection(x, y, time, missing=0.0, minlen=5, maxvel=3500, maxacc=100000,smi=False):
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

    if smi:
        minlen*=1000

    # INTER-SAMPLE MEASURES
    # the distance between samples is the square root of the sum
    # of the squared horizontal and vertical interdistances
    intdist = (np.diff(x)**2 + np.diff(y)**2)**0.5
    # get inter-sample times
    inttime = np.diff(time)
    # recalculate inter-sample times to seconds
    if smi:
        inttime = inttime / 1000000.0
    else:
        inttime = inttime / 1000.0


    # VELOCITY AND ACCELERATION
    # the velocity between samples is the inter-sample distance
    # divided by the inter-sample time
    vel = intdist / inttime
    # print(vel.shape)
    # print(intdist.shape)
    # print(inttime.shape)
    # the acceleration is the sample-to-sample difference in
    # eye movement velocity
    vel_dif=np.diff(vel)
    # print(vel_dif.shape)
    # vel_dif = np.insert(vel_dif,0,0)
    acc = np.divide(vel_dif,np.delete(inttime,0))

    # print("intdist")
    # print(np.mean(intdist))
    # print(np.std(intdist))
    # print(np.max(intdist))
    # print(np.min(intdist))
    # print("inttime")
    # print(np.mean(inttime))
    # print(np.std(inttime))
    # print(np.max(inttime))
    # print(np.min(inttime))
    # print("vel")
    # print(np.mean(vel))
    # print(np.std(vel))
    # print(np.max(vel))
    # print(np.min(vel))
    # print("acc")
    # print(np.mean(acc))
    # print(np.std(acc))
    # print(np.max(acc))
    # print(np.min(acc))

    # SACCADE START AND END
    t0i = 0
    stop = False
    while not stop:
        # saccade start (t1) is when the velocity or acceleration
        # surpass threshold, saccade end (t2) is when both return
        # under threshold

        # detect saccade starts
        sacstarts = np.where((vel[1+t0i:] > maxvel).astype(int) + (acc[t0i:] > maxacc).astype(int) >= 1)[0]
        # sacstarts = np.where((vel[1+t0i:] > maxvel).astype(int) == 1)[0]
        if len(sacstarts) > 0:
            # timestamp for starting position
            t1i = t0i + sacstarts[0] + 1
            if t1i >= len(time)-1:
                t1i = len(time)-2
            t1 = time[t1i]

            # add to saccade starts
            Ssac.append([t1])
            # print("Start",t1)

            # detect saccade endings
            sacends = np.where((vel[1+t1i:] < maxvel).astype(int) + (acc[t1i:] < maxacc).astype(int) == 2)[0]
            # sacends = np.where((vel[1+t1i:] < maxvel).astype(int) == 1)[0]
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
                    d = get_saccade_distance(gazepoints)
                    # add to saccade ends
                    # if smi:
                    #     print("End",dur/1000)
                    # else:
                    #     print("End",dur)
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


def offlinefix(x, y, time, smi=False,N=5):
    """
    Simply run the algorithm offline, i.e., on the entire list of gaze samples
    Returns a list of Efix (end fixation information, see fixation_detection() above
    """
    EndFixations = []
    Sfix, Efix = fixation_detection(x, y, time, smi=smi,N=N)
    # print(Efix)
    for fix in Efix:
       EndFixations.append([fix])
    return EndFixations


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

            # print(myfixations_off)


            # mysaccades_off =  saccade_detection(x,y,time) ##fully offline
            # print('num_saccades -',len(mysaccades_off))


            # stats(id,x,y,time)

            # outputfile_off = '/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/EyeTrackingData/Fixations/' + id +'-Fixations.csv'
            sacfile_off = '/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/EyeTrackingData/Saccades/' + id +'-Saccades.csv'

            for N in [5,10,15,20]:

                myfixations_off =  offlinefix(x,y,time,smi=False,N=N) ##fully offline
                # print(N,id)
                outputfile_off = '/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/EyeTrackingData/Fixations/Tests/' + id +'-Fixations-'+str(N)+'.csv'

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

def avg(a,b):
    a=list(a)
    b=list(b)
    l = []
    assert len(a)==len(b)
    for i in range(len(a)):
        if math.isnan(a[i]):
            l.append(float('nan'))
        elif math.isnan(b[i]):
            l.append(a[i])
            print("b missing")
        else:
            l.append((a[i]+b[i])/2)
    return(l)


# eye_path='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2016/Eye Tracking Data/SMI Data/Corrected'
#
# date=dict()
# eye_start=dict()
# for file in os.listdir(eye_path):
#     if 'Raw' in file and file.split('.')[-1] =='csv':
#         id = file.split('-')[0].upper()
#         id = (id.split('_')[0] + id.split('_')[1]).upper()
#         with open(os.path.join(eye_path,file),'r') as f:
#             df = pd.read_csv(f, sep=',',skiprows=37)#skip to the data
#             df = df.loc[:,['Time','L POR X [px]','L POR Y [px]', 'R POR X [px]', 'R POR Y [px]']].dropna()
#             time = list(df['Time'])
#             x = avg(df['L POR X [px]'],df['R POR X [px]'])
#             y = avg(df['L POR Y [px]'],df['R POR Y [px]'])
#
#             myfixations_off =  offlinefix(x,y,time,smi=True) ##fully offline
#             # print(myfixations_off)
#
#             # mysaccades_off =  saccade_detection(x,y,time,smi=True) ##fully offline
#             # print("num_saccades - ", len(mysaccades_off))
#
#             # stats(id,x,y,time,smi=True)
#
#             # outputfile_off = '/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2016/Eye Tracking Data/SMI Data/Fixations/' + id +'-Fixations.csv'
#             sacfile_off = '/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2016/Eye Tracking Data/SMI Data/Saccades/' + id +'-Saccades.csv'
#
#
#             fl = open(outputfile_off, 'w')
#             writer = csv.writer(fl)
#             writer.writerow(['index','fix_start_time', 'fix_end_time', 'fix_duration', 'fix_x', 'fix_y'])
#             i = 0
#             for values in myfixations_off:
#                 # print(values)
#                 values[0].insert(0,i)
#                 writer.writerow(values[0])
#                 i+=1
#             fl.close()
# #
# #
#             # fl = open(sacfile_off, 'w')
#             # writer = csv.writer(fl)
#             # writer.writerow(['index','sac_start_time', 'sac_end_time', 'sac_duration', 'sac_distance', 'sac_start_x', 'sac_start_y', 'sac_end_x', 'sac_end_y'])
#             # i = 0
#             # for values in mysaccades_off:
#             #     # print(values)
#             #     values.insert(0,i)
#             #     writer.writerow(values)
#             #     i+=1
#             # fl.close()
