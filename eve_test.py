#!/usr/bin/env python3.7

import glob, os, re, time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
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
       combat[ship]['weapon'] = weapon		# this only needs to be set once
   else:   # in_out = out
     if (miss == True): 
       combat[ship][weapon]['misses'] += int(1)
     else:
       combat[ship][weapon]['hits']   += int(1)
       combat[ship][weapon]['damage'] += int(damage)
       lastship = ship 



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
   
   
         if re.search('combat', line) is not None:
   
            # count the lines processed from this file
            count += 1
   
            # we missed our shot
            match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) Your (.*) misses (.*) completely', line)
            if match_object:
               updatestats(match_object.group(4), match_object.group(3), 0, True, 'out') 
   
            # our target missed their shot
            match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) (.*) misses you completely', line)
            if match_object:
               updatestats(match_object.group(3), None, 0, True, 'in') 
   
            # we hit our target
            match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) (\d*) to (.*) - (.*) - (.*)$', line)
            if match_object:
               updatestats(match_object.group(4), match_object.group(5), match_object.group(3), False, 'out') 
               lastship = match_object.group(4) 
               lastweapon = match_object.group(5)
    
            # our target hit us
            match_object = re.search('\[ ([\d.]*) ([\d:]*) \] \(combat\) (\d*) from (.*) - (.*) - (.*)$', line)
            if match_object:
               updatestats(match_object.group(4), match_object.group(5), match_object.group(3), False, 'in') 
   
      position = f.tell()
      f.close
      #print (str(count) + ' lines processed - file position ' + str(position))

      display_stats()

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
   os.system('clear')
   bounty_sum = 0
   displayformat = " | {:>8,}  {:>6,}  {:>8,}  {:>8,}"
   headerformat  = displayformat.replace(",","")

   # Display the Output Title:
   line1 = str("").center(30) + str("Enemy Ship").center(38)
   line2 = str("{:30}" + headerformat).format("Ship", 'Misses', 'Hits', 'Damage', 'Average')

   for weapon in sorted(weapons):
      # do something
      #print(weapon)
      line1 = line1 + str(weapon).center(37)
      line2 = line2 + str(headerformat).format('Misses', 'Hits', 'Damage', 'Average').center(24)

   line2 = line2 + str(" | {:>6} {:>12}").format("Kiils", "Bounty")
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
              line = line + bcolors.OKGREEN + damage_string(displayformat, combat[ship][weapon]['misses'], combat[ship][weapon]['hits'], combat[ship][weapon]['damage']).center(24) + bcolors.ENDC
           else:
              line = line + damage_string(displayformat, combat[ship][weapon]['misses'], combat[ship][weapon]['hits'], combat[ship][weapon]['damage']).center(24)

      line = line + (" | {:>6,} {:>12,}").format(combat[ship]['kills'], combat[ship]['bounty'])
      print (line)
      bounty_sum += combat[ship]['bounty']

   line = "   " + str("").center(30) + str("").center(38)
   for weapon in sorted(weapons):
      line = line + str("").center(38)
   line = line + ("  {:>6} {:>12,}").format("", bounty_sum)


   print(bcolors.OKGREEN + line + bcolors.ENDC) 





#################################################################
#####                         MAIN                          #####
#################################################################

# path to the source directory
path="/cygdrive/C/Users/Chris/Documents/EVE/logs/Gamelogs"

weapons = {}   # define the hash to hold the types of weapons used
combat = {}    # define the hash to hold the combat stats
count = 0
lastship = ""
lastweapon = ""

file = newestfile (path)
readfile (file)


# Enhancements:
#
# 2. allow a command line argument to a specific file for test processing
#
# 3. allow a -now command line argument to move file pointer to end of file before the first scan (essentially a reset without non-blocking key reads)
#
# 4. add kill count beside bounty column
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
