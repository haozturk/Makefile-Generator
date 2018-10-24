#!/usr/bin/python

import os
import sys
import re
from collections import deque

class headers:
    def __init__(self):
        self.isIncluded = 0
        self.dir= "/" #directory of a header file
        self.name = "" #name of a header file

class cFiles:
    def __init__(self):
        self.list = [] #holds the string values of the used headerfiles' name
        self.dir = "/"	#directory of a c file
	self.name = "" #name of a c file

#contains custom c files
cList = []
#contains custom header files
headerList = []
qlist = deque( [ sys.argv[1] ] )
while qlist:
    currentdir =  qlist.popleft()
    dircontents = os.listdir(currentdir)
    for name in dircontents:
        currentitem = currentdir + "/" + name
        if os.path.isdir(currentitem):
            qlist.append(currentitem)
        else:
            if str(currentitem).endswith(".c"):
                currentCFile = cFiles() #a cFiles object is created
                currentCFile.dir = str(currentitem) #its dir field is initialized
		currentCFile.name = name #its name filed is initialized
                cList.append(currentCFile) #it's added to the cList
            elif str(currentitem).endswith(".h"):
                currentHFile = headers() #a cFiles object is created
                currentHFile.dir = str(currentitem) #its dir field is initialized
		currentHFile.name = name #its name filed is initialized
                headerList.append(currentHFile) #it's added to the cList

cFileNameList = [] #list that contains the names of all c files
headerNameList = [] #list that contains the names of the header files which are included in .c files, we'll use it to generate warning message if necessary
#traverses the .c files and finds and assigns their included header files
for curr in cList:
	f = open(curr.dir,'r') #.c file is opened
	# read the file line by line
	for line in f:
		#if the line is starts with #include look further
		if line[0:8] == '#include':
			headerFileName = re.search(r'\w*.h', line) #if you see a substring containing .h take that substring
			if headerFileName.group() != "stdio.h": #if the include is stdio.h, discard it
				curr.list.append(headerFileName.group()) #add the name of the header file into the list of the particular cFile
				headerNameList.append(headerFileName.group())
		
	f.close() #close the file

#generates a warning message if there is an unused header file
headerUsed = 0
for index in headerList:
	name = index.name
	headerUsed = 0
	for index2 in headerNameList:
		if name == index2:
			headerUsed = 1
	if headerUsed==0:
		print "WARNING: The headerFile named " + name + " " + "is not used."

#look if the included header file is present, if not generate an error message and halt the program
for i in headerNameList:
	headerFound = 0
	for j in headerList:
		if i == j.name:
			headerFound = 1
	if headerFound == 0:
		print "ERROR: The header " + i + " is not found."			
		sys.exit(0)

#WRITING THE MAKEFILE

make = open("makefile","w")
#the exe file
make.write("program: ")
#write the dependencies for the executable program
for i in cList:
	#dependent files are object files, write them according to the name of the c file
	make.write(i.name[0:len(i.name)-2] + ".o ") 
make.write("\n\t")
make.write("gcc ") #start of the gcc command
for i in cList:
	make.write(i.name[0:len(i.name)-2] + ".o ") #object files
make.write("-o program\n\n")

#in the following for loop targets which are the object files and their dependencies are written.
#After that corresponding gcc command is written
for i in cList:
	make.write(i.name[0:len(i.name)-2] + ".o: ") #write the target
	make.write(i.dir + " ") #first dependency which is the corresponding c file of the object file is written

	parentPath = "" #the directory where the included header files are located
	parentList = [] #keeps the directories of each header file of the current c file 	 	
	#directories of header files used in that particular .c file
	# this loop takes care of the header files of current c file
	for j in i.list:
		#we know the header name, but we should find its path from the headerList
		directory = ""
		for t in headerList:
			if t.name == j:
				directory = t.dir
				parentPath = directory[0:len(directory)-len(t.name)-1]
				parentList.append(parentPath)
		make.write(directory + " ")
	make.write("\n\t")
	parentSet = set(parentList) #duplicate directories are removed
	#gcc command
	make.write("gcc -c ")
	for s in parentSet:
		make.write("-I " + s + " ")
	make.write(i.dir)
	make.write("\n\n")

make.close() #close the makefile file

