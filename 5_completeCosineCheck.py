"""
5_completeCosine Check is part of a series of programs to detect spoofing attacks
The current focus is on replay attacks
"""

#Get libraries
import math
import re
from collections import Counter
import sqlite3 as lite
import os

WORD = re.compile(r"\w+")


def get_cosine(vec1, vec2):
   intersection = set(vec1.keys()) & set(vec2.keys())
   numerator = sum([vec1[x] * vec2[x] for x in intersection])
   sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
   sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
   denominator = math.sqrt(sum1) * math.sqrt(sum2)    
   if not denominator:
      return 0.0
   else:
      return float(numerator) / denominator
    
    
def text_to_vector(text):
   words = WORD.findall(text)
   return Counter(words)

def compare_all(oList, inICAO):
   #this function assumes the replay message set 
   #is in the replay.txt file 
   #function main should put it there
   cutoff_len = .3*len(oList)
   replay = ""
   for item in oList:
      replay = replay + item
   vector1 = text_to_vector(replay)
   #vector 1 is the replay attack set of messages
   original = ""
   #original is the holder for a mnatch set of messages 
   #we get for each ICAO
   #it must be reset each time thru
   q = "SELECT distinct ICAO, msg FROM adsb order by ICAO;"

   my_cursor=cur.execute(q)
   results = my_cursor.fetchall()
   lenRS = len(results)
   loopICAO = 'Start'
   iList = []
   if lenRS > cutoff_len:
      for row in results:
        if loopICAO != row[0]:
           vector2 = text_to_vector(original) 
           cosine = get_cosine(vector1, vector2)
           if cosine > 0: 
              print("These ICAOs ", inICAO, loopICAO, " have cosine ", cosine, "\n")
              cosFile.write(holdICAO + ", " + loopICAO + ", " + str(cosine) + '\n')  
              cosFile.flush()  
              os.fsync(cosFile.fileno()) 
           loopICAO = row[0]
           original = row[1] + "\n"
        else:
           original = original + row[1] + "\n" #to match file read

"""
MAIN
This program calculates the cosine of each ADSB record that was captured
against each of the other 2,127 records (2,128 records total)
The prupose is to find the maximum cosine that results from
natuarrraly occuring duplicates in the ADSB message traffic
A loop is setup to loop thru the unioque ICAOs in the traffic table and then for the selected ICAO loop tghrough all the ICAOs and
calculate the cosine. 
A cosine of 1 will occur whejn the outer ICAO is compared to itself
as the ICAO in the inner loop. All other cosines will be the result 
of ntaurally occuring duiplicates
once comapred withj all other ICAOs in the inner loop, that outer loop ICAO is deleted so that its matches are not double counted
the number of computations equals n*(n-1)/2 or for this case
2,128 * 2,127 /2 = 2,263,128
"""

#Open database connection and output file
con = lite.connect('adsb.msg')
cur = con.cursor()
print("Successfully Connected to SQLite")
#filename = "replay.txt"
cosFile = open('newCosines.txt', 'a')

#compare_all()

#to do queries
#1. select distinct ICAO from adsb;
#2.  write this to replay file
#3. call compare_all()

q = "SELECT distinct ICAO, msg FROM adsb order by ICAO;"
cur2=cur.execute(q)
rs = cur2.fetchall()
#refile = open(filename, 'w')
oList = []
holdICAO = 'Start'
for gmrICAO in rs:
   #print(gmrICAO)
   if holdICAO != gmrICAO[0]:
      print("starting another ICAO", gmrICAO[0])
      #refile.close()
      if holdICAO != 'Start':
         compare_all(oList, holdICAO)
      #refile = open(filename, 'w')
      oList = []
      #refile.write(gmrICAO[1] + '\n')
      oList.append(gmrICAO[1] + '\n')
      q4 = "delete from adsb where ICAO = '" + holdICAO + "';"
      cur4 = cur.execute(q4)
      con.commit()
      print("after delete")
      holdICAO = gmrICAO[0]
   else:
      #refile.write(gmrICAO[1] + '\n')
      oList.append(gmrICAO[1] + '\n')
cosFile.close()


