import numpy as np
import os.path
import sys
import time

#RIGHT NOW THE FEATURES MAJOR, SCHOOL, AND COURSES NEED TO BE MANUALLY DELETED 
#FROM NatashaActionFeatures.csv BEFORE RUNNING THIS SCRIPT

"""Here are the list of features that need to be removed (because they are 
highly correlated with another feature or could lead to overfitting)
Feature																Column
==========================================================================
Name																2
#Subgoal changes													14
#TN																	22
#RR																	24
#COIS																25
#Unknown															32
Mean of SRL processes per relevant page while on Subgoal 0			33"""
listOfFeatures2Remove = [2, 14, 22, 24, 25, 32, 33]

def getGroupCode(str):
	if str == "Control":
		return '1'
	elif str == "Feedback":
		return '2'
	else:
		return '-1'

def getGenderCode(str):
	if str == "Female":
		return '1'
	elif str == "Male":
		return '2'
	else:
		return '-1'
		
def getEthnicityCode(str):
	if str == "Asian":
		return '1'
	elif str == "White/ Caucasian":
		return '2'
	elif str == "Spanish/Hispanic/Latino":
		return '3'
	elif str == "Other":
		return '4'
	else:
		return '-1'
		
def getEducationCode(str):
	if str == "Freshman":
		return '1'
	elif str == "Sophomore":
		return '2'
	elif str == "Junior":
		return '3'
	elif str == "Senior":
		return '4'
	else:
		return '1'

def getBoolCode(str):
	if str == "TRUE":
		return '1'
	else:
		return '0'

folder = "C:\\Users\\admin\\Dropbox\\Research\\InteractionLogs\\MetaTutorLogParser\\MTLogAnalyzer\\"
outfile_name = folder + "NatashaActionFeaturesCoded.csv"
outfile = open(outfile_name, 'w')

infile_name = folder + "NatashaActionFeatures.csv"

if os.path.exists(infile_name):
	#open and read input files 
	infile = open(infile_name, 'r')
	lines = infile.readlines()
	
	for l in range(len(lines)): 
		words = lines[l].split(",")
		
		for w in range(len(words)-1): 		#ignore endline
			if w in listOfFeatures2Remove:
				continue; #skip features we wish to remove
			elif l != 0: 						#skip row of labels
				if w == 1: #group
					outfile.write(getGroupCode(words[w])+ ", ")
				elif w == 3: #gender
					outfile.write(getGenderCode(words[w])+ ", ")
				elif w == 5: #ethnicity
					outfile.write(getEthnicityCode(words[w])+ ", ")
				elif w == 6: #education
					outfile.write(getEducationCode(words[w])+ ", ")
				elif w == 13: #worked without subgoal
					outfile.write(getBoolCode(words[w])+ ", ")
				elif words[w] == "inf" or words[w] == "nan" or words[w] == "N/A":
					outfile.write("?, ")
				else:
					outfile.write(words[w] + ", ")
			else:
				outfile.write(words[w] + ", ")
		outfile.write("\n")
		
	infile.close()
else:
	print "Error: Couldn't open input files"
outfile.close()
