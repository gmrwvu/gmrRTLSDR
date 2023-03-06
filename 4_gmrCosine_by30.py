"""
4_gmrCosine_by30 is the detection progrtam
Current status: in progress
working with just an ICAO in a text file to develop and verify the detction algorithmk
"""

#Get libraries
import math
import re
from collections import Counter
import sqlite3 as lite

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
   print("Length of words ", len(words))
   return Counter(words)

def gmrPrep(r_icao, icao, rList, mList): 
   print("Cosine follows for these ICAOs", r_icao, icao)
   mLine = ' '.join(mList)
   rLine = ' '.join(rList)
   replay = ""
   original = ""

   for item in mLine:
      original = original + item

   for item in rLine:
      replay = replay + item

   print("Length of replay str :", len(replay)) #number of lines in replay.txt * len of line
   print("Length of match str : ", len(original))   
   vector1 = text_to_vector(replay)
   vector2 = text_to_vector(original)
   print("Length of vec1 :", len(vector1))
   print("Length of vec2 : ", len(vector2))   

   cosine = get_cosine(vector1, vector2)
   print("Cosine:", cosine)
 

#ALSO PUT IN CHECK IS ROW CNT HERE IS LESS THAN 30% OF ROW CNT FOR REPLAY
#THEN BREAK
#bug here is I am putting all the icaos in the same match file
#I should be making a list of lists 
#or cosine comparing each mList returned 
def save_replay(icao):
   mList = []
   q = "SELECT msg FROM adsb WHERE icao ='" + icao + "';"
   rply_cursor=cur.execute(q)
   rply = rply_cursor.fetchall()
   print("Length of cursor is ", len(rply))
   for m_row in rply:
       mList.append(m_row[0])
   return mList

#Open database connection and output file
con = lite.connect('adsb.msg')
cur = con.cursor()
print("Successfully Connected to SQLite")

#Next read in the replay text file and find if it has a match
#get a count on number of matches
filename = "replay.txt"
myfile = open(filename, 'r')

#for program dev I used these two ICAOs
#They are the values in the Replay file
#WYHEN YOU SWITCH THESE YOU MUST RERUN 4_GMRCOSINE
#gmrICAO = 'C023B7'
gmrICAO = 'ACBF63'

lines = myfile.readlines()
print("replay count ", len(lines))
cnt = 0
replayICAO = 'Start'

#make a list for replay
rList = []
for line in lines:
    rList.append(line[:-1])#strip off crlf
# receive msg from the server
#if have rowcount 1 or more, then use icao to get all
#msg's that may be related

#FOR TESTING - REPLAY.TXT for l;ong HAS 540 REOORDS THAT MATCH
#THE 540 RECORDS IN ADSB FOR ACBF63
#the replay for short has 45

alreadyChecked = []
for line in lines:
   replay = line[:-1]
   q = "SELECT icao, msg FROM adsb WHERE msg ='" + replay + "';"
   my_cursor=cur.execute(q)
   rs = my_cursor.fetchall()
   #print("length of rs for", replay, " is", len(rs))
   cnt = cnt + 1
   for row in rs:      #need to account for multiple rows for a msg val
      print("ICAO is ", row[0])
      if replayICAO != row[0]:
         if row[0] not in alreadyChecked:
            replayICAO = row[0]
            mList = save_replay(row[0])
            gmrPrep(gmrICAO, row[0], rList, mList)
            alreadyChecked.append(row[0])
print("Replay lines looped", cnt)
myfile.close()
con.close()
print("already chacked", alreadyChecked)
