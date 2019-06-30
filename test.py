#!/usr/bin/env python3.7

import glob, os, re

def updatestats(ship, weapon, damage, miss, in_out):
   # ship = enemy type
   # weapon = drone/weapon used by us
   # damage = # of points damage
   # miss = did we/they miss?


   # predefine all of the hash variables so we don't need to existance test them later
   if ship not in combat.keys():
      combat[ship] = {}
      combat[ship]['misses_in'] = 0
      combat[ship]['misses_out'] = 0
      combat[ship]['shots_in'] = 0
      combat[ship]['shots_out'] = 0
      combat[ship]['damage_in'] = 0
      combat[ship]['damage_out'] = 0
      combat[ship]['bounty'] = 0

   if (in_out == 'in'):
     if (miss == True): 
       combat[ship]['misses_in'] += int(1)
     else:
       combat[ship]['shots_in'] += int(1)
       combat[ship]['damage_in'] += int(damage)
   else:   # in_out = out
     if (miss == True): 
       combat[ship]['misses_out'] += int(1)
     else:
       combat[ship]['shots_out'] += int(1)
       combat[ship]['damage_out'] += int(damage)
       lastship = ship 



def readfile (filename):
   f = open(filename,"r")
   lastship = ""

   for line in f:
      # remove the colorizing in each line
      line = re.sub('<.*?>', '', line)

      if re.search('bounty', line) is not None:
         # lastship should be defined (bounty for something we haven't shot at yet??)
         line = re.sub(',', '', line)  # de-comma-ize the money values

         # [ 2019.04.04 18:08:33 ] (bounty) 18,168.75 ISK added to next bounty payout
         match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(bounty\) (.*) ISK added to next bounty payout', line)
         combat[lastship]['bounty'] += int(float(match_object.group(3)))


      if re.search('combat', line) is not None:

         # count the lines processed from this file
         combat['count'] += 1

         # we missed our shot
         match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) Your (.*) misses (.*) completely', line)
         if match_object:
            updatestats(match_object.group(4), match_object.group(3), 0, True, 'out') 

         # our target missed their shot
         match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) (.*) misses you completely', line)
         if match_object:
            updatestats(match_object.group(3), "", 0, True, 'in') 

         # we hit our target
         match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) (\d*) to (.*) - (.*) - (.*)$', line)
         if match_object:
            updatestats(match_object.group(4), match_object.group(5), match_object.group(3), False, 'out') 
            lastship = match_object.group(4) 
 
         # our target hit us
         match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) (\d*) from (.*) - (.*) - (.*)$', line)
         if match_object:
            updatestats(match_object.group(4), match_object.group(5), match_object.group(3), False, 'in') 



   f.close
   print (str(combat['count']) + ' lines processed')



def newestfile (path):
   os.chdir(path)
   
   list_of_files = glob.glob(path + '/*.txt') # * means all if need specific format then *.csv
   latest_file = max(list_of_files, key=os.path.getctime)
   return (latest_file)


def display_stats():
   bounty_sum = 0

   for ship in sorted(combat):
      if ship != 'count':
          # watch out for a ship that has shot us but we have not yet shot at
          if (combat[ship]['shots_out'] == 0):
             avgdmg = 0
             print ("{:40} damage: {:8}   shots:  {:6}   avg dmg:  {:6}    bounty:  {:8}".format(ship, 0, 0, avgdmg, 0))
          else:
             avgdmg = int(combat[ship]['damage_out'] / combat[ship]['shots_out'])
             print ("{:40} damage: {:8}   shots:  {:6}   avg dmg:  {:6}    bounty:  {:>12,}".format(ship, combat[ship]['damage_out'], combat[ship]['shots_out'], avgdmg, combat[ship]['bounty']))
             bounty_sum += combat[ship]['bounty']

   print ("{:40}         {:8}           {:6}             {:6}             {:>12}".format("","","","","-------------"))
   print ("{:40}         {:8}           {:6}             {:6}             {:>12,}".format("","","","", bounty_sum))




#################################################################
#####                         MAIN                          #####
#################################################################


path="/cygdrive/C/Users/Chris/Documents/EVE/logs/Gamelogs"

combat = {}   # define the hash to hold the combat stats
combat['count'] = 0
lastship = ""

file = newestfile (path)
readfile (file)
display_stats()


# Enhancements:
#
# 1. Add to git
#
# 2. need to clean up the summary table at the bottom, reflect inbound/outbound data separately
#      - change to an output function, this will facilitate 4&5 below
#
# 3. need to expand combat dictionary variable to track by weapon type
#      - outbound damage only?
#
# 4. need to adjust the file read/seek logic to track the size/end of the file, and loop until cancelled
#      - allows us to lighten the overhead by the script
#
# 5. use ansi commands to reflect color on the output lines
#      - combine this with change #3 above, use lastship variable to highlight which target was last shot at
#
# 6. allow a "from now" flag to be entered on the keyboard
#      - this would allow you to flag the start of a new site
#      - maybe track bounties over flags
#      - include a reset back to full output flag as well
