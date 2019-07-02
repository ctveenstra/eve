#!/usr/bin/env python3.7

import glob, os, re, time, getopt
from time import strptime
from time import gmtime
from time import mktime
from datetime import timedelta

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def updatestats(ship, weapon, damage, miss, in_out):
   # ship = enemy type
   # weapon = drone/weapon used by us
   # damage = # of points damage
   # miss = did we/they miss?

   # predefine the base hash variables so we don't need to existance test them later
   if ship not in combat.keys():
      combat[ship] = {}
      combat[ship]['bounty'] = 0

      # Inbound attacks - they only use 1 kind of weapon - need to validate this
      combat[ship]['misses'] = 0
      combat[ship]['hits'] = 0
      combat[ship]['damage'] = 0
      combat[ship]['weapon'] = None
      combat[ship]['kills'] = 0
 
   # Check if this weapon hash structure exists yet, define it if not
   if weapon is not None and in_out == 'out':
      if (combat[ship].get(weapon, {}).get('misses', None) is None):		# check if new weapon used
         combat[ship][weapon] = {}
         combat[ship][weapon]['misses'] = 0
         combat[ship][weapon]['hits'] = 0
         combat[ship][weapon]['damage'] = 0

         # keep track of the distinct weapons used (to populate the output table later)
         if (weapon not in weapons.keys()):
            weapons[weapon] = weapon

   # process the attack
   if (in_out == 'in'):
     if (miss == True): 
       combat[ship]['misses'] += int(1)
     else:
       combat[ship]['hits']   += int(1)
       combat[ship]['damage'] += int(damage)
       combat[ship]['weapon'] = weapon		# this actually only needs to be set once
   else:   # in_out = out
     if (miss == True): 
       combat[ship][weapon]['misses'] += int(1)
     else:
       combat[ship][weapon]['hits']   += int(1)
       combat[ship][weapon]['damage'] += int(damage)
       lastship = ship 


# takes date and time strings from log file, builds time_struct from them
def timestamp (strdate, strtime):
   # need to be able to clear some of these structures, as needed
   global starttime
   global lasttime
   global combat
   global weapons

   # build a time_struct representing the current log entry timestamp
   current = strptime(strdate + " " + strtime, '%Y.%m.%d %H:%M:%S')

   # make sure the start time is the first time in the log file (essentially pull the first entry)
   if (mktime(starttime) > (mktime(current))):
      starttime = current

   # determine the offset between the last message and the current message (in seconds)
   delta = mktime(current) - mktime(lasttime)

   # if we have a delta > say 30 seconds, this means:
   #   we had a lull in the fight, but the fight has since resumed (say moved to a new haven site)
   #   this would be a good time to reset the counters (based on timeout setting)
   if (delta > timeout):
      print ("Delta (" + str(delta) + " > " + str(timeout) + ", clearing dictionaries")
      weapons.clear()   # reset the hash to hold the types of weapons used
      combat.clear      # reset the hash to hold the combat stats
      count = 0
      lastship = ""
      lastweapon = ""
      starttime = current
      lasttime = current 

   # check if the log time is more recent than the last time we saw (compensating for GMT)
   if (mktime(current) > (mktime(lasttime) - tzoffset)):
      lasttime = current



def readfile (filename):
   global count
   lastship = ""
   lastweapon = ""
   position = 0

   while True:
      f = open(filename,"r")
      f.seek(position)

      for line in f:
         # remove the colorizing in each line
         line = re.sub('<.*?>', '', line)
   
         if re.search('bounty', line) is not None:
            # lastship should be defined (bounty for something we haven't shot at yet??)
            line = re.sub(',', '', line)  # de-comma-ize the money values
   
            # [ 2019.04.04 18:08:33 ] (bounty) 18,168.75 ISK added to next bounty payout
            match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(bounty\) (.*) ISK added to next bounty payout', line)
            combat[lastship]['bounty'] += int(float(match_object.group(3)))
            combat[lastship]['kills'] += 1
            timestamp (match_object.group(1), match_object.group(2))
   
   
         if re.search('combat', line) is not None:
            # count the lines processed from this file
            count += 1
   
            # we missed our shot
            match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) Your (.*) misses (.*) completely', line)
            if match_object:
               updatestats(match_object.group(4), match_object.group(3), 0, True, 'out') 
               timestamp (match_object.group(1), match_object.group(2))
   
            # our target missed their shot
            match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) (.*) misses you completely', line)
            if match_object:
               updatestats(match_object.group(3), None, 0, True, 'in') 
               timestamp (match_object.group(1), match_object.group(2))
   
            # we hit our target
            match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) (\d*) to (.*) - (.*) - (.*)$', line)
            if match_object:
               updatestats(match_object.group(4), match_object.group(5), match_object.group(3), False, 'out') 
               timestamp (match_object.group(1), match_object.group(2))
               lastship = match_object.group(4) 
               lastweapon = match_object.group(5)
    
            # our target hit us
            match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) (\d*) from (.*) - (.*) - (.*)$', line)
            if match_object:
               updatestats(match_object.group(4), match_object.group(5), match_object.group(3), False, 'in') 
               timestamp (match_object.group(1), match_object.group(2))

      position = f.tell()
      f.close

      display_stats()

      #systime.sleep(1)
      time.sleep(1)


def newestfile (path):
   os.chdir(path)
   
   list_of_files = glob.glob(path + '/*.txt') # * means all if need specific format then *.csv
   latest_file = max(list_of_files, key=os.path.getctime)
   return (latest_file)


def damage_string(form, m, h, d):
   if (h > 0):
     ad = int(d / h)
   else:
     ad = 0

   ds = (form.format(m, h, d, ad))
   return ds



def display_stats():
   global starttime
   global lasttime

   os.system('clear')
   bounty_sum = 0
   # Display Format:   miss     hit    damage   avgdmg
   displayformat = " | {:>6,}  {:>6,}  {:>10,}  {:>8,}"
   headerformat  = displayformat.replace(",","")

   # Display the Output Title:
   line1 = str("").center(30) + str("Enemy Ship").center(38)
   line2 = str("{:30}" + headerformat).format("Ship", 'Misses', 'Hits', 'Damage', 'Average')

   for weapon in sorted(weapons):
      # do something
      #print(weapon)
      line1 = line1 + str(weapon).center(37)
      line2 = line2 + str(headerformat).format('Misses', 'Hits', 'Damage', 'Average').center(24)

   line2 = line2 + str(" | {:>6} {:>12}").format("Kills", "Bounty")
   print (line1)
   print (line2)

   # iterate through the dataset
   for ship in sorted(combat):
      # watch out for a ship that has shot us but we have not yet shot at
      if (combat[ship]['hits'] == 0):
         avgdmg = 0
      else:
         avgdmg = int(combat[ship]['damage'] / combat[ship]['hits'])
 
      line = ("{:30}".format(ship) + damage_string(displayformat, combat[ship]['misses'], combat[ship]['hits'], combat[ship]['damage']))

      for weapon in sorted(weapons):
         # do something
         if (combat[ship].get(weapon, {}).get('hits', None) is None):		# check if new weapon used
            line = line + " |" + str("").center(37)
         else:
           if combat[ship][weapon]['hits'] == 0:
              avgdmg = 0
           else:
              avgdmg = int(combat[ship][weapon]['damage'] / combat[ship][weapon]['hits'])
           
           if (ship == lastship and weapon == lastweapon):
              line = line + bcolors.GREEN + damage_string(displayformat, combat[ship][weapon]['misses'], combat[ship][weapon]['hits'], combat[ship][weapon]['damage']).center(24) + bcolors.ENDC
           else:
              line = line + damage_string(displayformat, combat[ship][weapon]['misses'], combat[ship][weapon]['hits'], combat[ship][weapon]['damage']).center(24)

      line = line + (" | {:>6,} {:>12,}").format(combat[ship]['kills'], combat[ship]['bounty'])

      print (line)
      bounty_sum += combat[ship]['bounty']

   line = "   " + str("").center(30) + str("").center(38)
   for weapon in sorted(weapons):
      line = line + str("").center(38)
   line = line + ("  {:>6} {:>12,}").format("", bounty_sum)

   print(bcolors.GREEN + line + bcolors.ENDC) 

   print("")
   print("Now:         " + time.asctime(gmtime()))
   print('Start Time:  ' + time.asctime(starttime))
   print('Last Time:   ' + time.asctime(lasttime))

   # can we determine the offset between now and the last message
   delta = mktime(lasttime) - mktime(starttime)
   a = timedelta(seconds=delta)
   print('Elapsed Time ' + str(a))

#################################################################
#####                         MAIN                          #####
#################################################################

# path to the source directory
path="/cygdrive/C/Users/Chris/Documents/EVE/logs/Gamelogs"
tzoffset=3600
timeout=60

weapons = {}   # define the hash to hold the types of weapons used
combat = {}    # define the hash to hold the combat stats
count = 0
lastship = ""
lastweapon = ""
starttime = strptime("2100.01.01 01:00:00", '%Y.%m.%d %H:%M:%S')   # dummy future start time
lasttime = strptime("2000.01.01 01:00:00", '%Y.%m.%d %H:%M:%S')    # dummy historical current time

# find the most recent log file in the Gamelogs directory
file = newestfile (path)

# process the file
readfile (file)


# Enhancements:
#
# 2. allow a command line argument to a specific file for test processing
#
# 3. allow a -now command line argument to move file pointer to end of file before the first scan (essentially a reset without non-blocking key reads)
#
# 5. use ansi commands to reflect color on the output lines
#      - combine this with change #3 above, use lastship variable to highlight which target was last shot at
#      - add a function to scan the dictionary to determine the ship with the highest average damage, use this for the colorizing
#
# 6. allow a "from now" flag to be entered on the keyboard
#      - this would allow you to flag the start of a new site
#      - maybe track bounties over flags
#      - include a reset back to full output flag as well
#
# 7. colorizing - with multiple outbound damage types, highlight which avgdmg is highest between the types
#      - this indicates the preferred weapon for each target type
#
# 8. optionally offer a sort by feature - highest average incoming damage, alphabetical, etc.
#
# 9. detect start/end times for the sites, automatically show the start time, end time, and elapsed duration
#      - reset the start time after some period of no hit detection (default window of like 1 minute or something)
#
#
# Bugs:
# 
#  - there appears to be an issue during fresh runs, inbound enemy activity is not being recorded, all 0's despite us shooting back
#    - only populating on hits, not on misses?
