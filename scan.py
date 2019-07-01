#!/usr/bin/env python3.7

import glob, os, re

def readfile (filename):
   f = open(filename,"r")

   for line in f:
      if re.search('combat', line) is not None:

         # remove the colorizing in the combat lines
         line = re.sub('<.*?>', '', line)

         # we missed our shot
         match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) Your (.*) misses (.*) completely', line)
         if match_object:
            print (match_object.group(1) + " " + match_object.group(2) + ":  " + match_object.group(3) + " misses " + match_object.group(4))

         # our target missed their shot
         match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) (.*) misses you completely', line)
         if match_object:
            print (match_object.group(1) + " " + match_object.group(2) + ":  " + match_object.group(3) + " misses")

         # we hit our target
         match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) (\d*) to (.*) - (.*) - (.*)$', line)
         if match_object:
            print (match_object.group(1) + " " + match_object.group(2) + ":  " + match_object.group(3) + " damage to " + match_object.group(4) + " by " + match_object.group(5) + " : " + match_object.group(6))
 
         # our target hit us
         match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) (\d*) from (.*) - (.*) - (.*)$', line)
         if match_object:
            print (match_object.group(1) + " " + match_object.group(2) + ":  " + match_object.group(3) + " damage from " + match_object.group(4) + " by " + match_object.group(5) + " : " + match_object.group(6))

   f.close




path="/cygdrive/C/Users/Chris/Documents/EVE/logs/Gamelogs"

os.chdir(path)

for file in glob.glob("*.txt"):
    date, time = file.split("_")
    time, x = time.split(".")
    
    # print("File: {}   Date: {}   Time:  {}".format(file,date,time))
    filename = path + "/" + file
    # print(filename)
    x = readfile (filename)



