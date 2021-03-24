import csv
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

# Define a filename.
filename = dir_path+'/output.txt'

# Open the file as f.
# The function readlines() reads the file.
with open(filename) as f:
    content = f.readlines()

# Show the file contents line by line.
# We added the comma to print single newlines and not double newlines.
# This is because the lines contain the newline character '\n'.
ss=[]
for line in content:
    if line != '\n':
        line = line.split('\n')[0]
        if 'self.starting' in line:
            ss.append(line.split(' ')[-2])
ss=sorted(set(item for item in ss if item != ''))
print(ss)
