import sys  # command line
import re   # regular expression tools
import os   # checking if file exists
import subprocess   # executing program

# get files
inputFname = sys.argv[1] 
outputFname = sys.argv[2]

# create dictionary
dictionary = dict()

print("Counting words...")
# read from input file
with open(inputFname, "r") as textInputFile:
    # use regex to get words and ignore punctuation
    words = (re.split(r"\s*[.]*[,]*[;]*[:]*[\"]*[']*[-]*", textInputFile.read()))
    for word in words:
	if not word == "":
                word = word.lower() # change words to lowercase
		if word in dictionary:
			dictionary[word] += 1 # if word is repeated, increase count
		else:
			dictionary[word] = 1 # if first occurrence, set count to 1
    textInputFile.close() # close file
    
# write on output file
with open(outputFname, "w+") as textOutputFile:
    for w in sorted(dictionary):
        textOutputFile.write("%s %s" % (w, dictionary[w]) + "\n") # write in file with format: '#OfOcurrences word'
    textOutputFile.close() # close file
print("Word count finished.")