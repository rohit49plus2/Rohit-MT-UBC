import numpy as np
import os.path
import sys
import time

#Set up 
class1 = "emotionPresent"
class2 = "emotionAbsent"

user = "admin"

debug = False

emotion = "boredom" # could be "curiosity" or "boredom"
if len(sys.argv) >= 2:
    emotion = sys.argv[1]

	
#File Paths
folder = "C:\\Users\\" + user + "\Dropbox\\Research\\InteractionLogs\\MetaTutorLogParser\\MTLogAnalyzer\\"
outfile_name = folder + "NatashaActionFeatures-"+emotion+".arff"
outfile = open(outfile_name, 'w')

infile_name = folder + "NatashaActionFeaturesCoded.csv"
emot_file_name = folder + "EmotionReportData-Excl21PlusAvgsPlusScenes.csv"


#Deal with files
if os.path.exists(emot_file_name) and  os.path.exists(infile_name):
	#open and read input files 
	infile = open(infile_name, 'r')
	lines = infile.readlines()
	emot_file = open(emot_file_name, 'r')
	emot_lines = emot_file.readlines()
	
	if debug: print "There are", len(emot_lines), "in emotion file" 
	if debug: print "There are", len(lines), "in data file" 
	
	#write the relation name
	outfile.write("@relation '"+ emotion + "InteractionRelation'\n\n")
	
	#write the names of attributes
	attributes = lines[0].split(","); #first line contains attribute names
	for i in range(1, len(attributes) - 1): #skip endline character
		outfile.write("@attribute '" + attributes[i] + "' numeric\n")

	outfile.write("@attribute cluster {" + class1 + "," + class2 + "}\n")

	
	#write the data and labels
	outfile.write("\n@data\n\n")
	
	label_index = 0 #to match features from data file with emotion self report for same participant
	for l in range(1,len(lines)): 
		if debug: print "on data line", l
		if debug: print "on emotion line", label_index
		words = lines[l].split(",") #get next set of features
		
		#Exclude participant with no emotion self-reports
		if words[0] == "MT208PN41077":
			continue
			
		#Exclude participants with inconsistent averaged self-reports
		if words[0] == "MT208PN41055" or words[0] == "MT208PN41059" or words[0] == "MT208PN41061" or words[0] == "MT208PN41081":
			continue
			
		#PRINT FEATURES
		for w in range(1,len(words)-1): 		#skip participant id #ignore endline
			if words[w] == "inf" or words[w] == "nan" or words[w] == "N/A" or words[w] == "X":
				outfile.write("?, ")
			else:
				outfile.write(words[w] + ", ")
		
		#FIND CORRECT EMOTION LABEL		
		emot_words = emot_lines[label_index].split(",") #get index into next participant in emotion label file
		while emot_words[0] != words[0]: #check if participant names don't match in data and label
			#if debug: print "comparing data file:", words[0], "and emot file:", emot_words[0]
			label_index = label_index + 1 #skip this participant's emotion event
			if debug: print "No valid eye tracking data for ppt", emot_words[0], "at time", emot_words[1]
			emot_words = emot_lines[label_index].split(",")
		while emot_words[1] != "scene4": #check if scenes don't match
				label_index = label_index + 1 #skip this participant's emotion event
				if debug: print "Scenes do not match, skipping emotion report", emot_words[1]
				emot_words = emot_lines[label_index].split(",")

		#get label for this data point
		if emotion == "boredom":
				emot_value = emot_words[len(emot_words)-2]
		elif emotion == "curiosity":
				emot_value = emot_words[len(emot_words)-1]
		else:
				print "Error: invalid emotion"
		print "Average", emotion, "report value for", words[0], "was", emot_value

		
		#CHOOSE LABELS BASED ON MEDIAN SPLIT
		if emotion == "boredom":
			cutoff = 2.6 #median for boredom
		elif emotion == "curiosity":
			cutoff = 2.8 #median for curiosity		
		
		if float(emot_value) >= cutoff:
			label = class1
		elif float(emot_value) < cutoff:
			label = class2
			
		outfile.write("'" + label + "'\n")
		label_index = label_index + 1
		
	infile.close()
else:
	print "Error: Couldn't open input files"
outfile.close()
