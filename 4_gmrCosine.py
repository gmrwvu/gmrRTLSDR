"""
This progra does the detecting
In its first version it does the following
1. reads a set of messages from the database
   fro an ICAO with many duplicates 
2. writes that result set to an os file
3. try files withj all mesagse and also where
   an portion of the messages taken oput
4. Next select the records in the database 
   that equal the 56-bit message of the incoming
   112 extended squitter message with header data
5. If get some recorsd in the result set
   read all recoerds for the ICAO for each
   such result record one at a time
   and p[erform the cosine similarity check
6. This has been validated in teh 5_completeCosien Check py 

"""

#Get libraries
import math
import re
from collections import Counter
import sqlite3 as lite

def save_replay(icao):
   print("got a match", icao)
   q = "SELECT msg FROM adsb WHERE icao ='" + icao + "';"
   rply_cursor=cur.execute(q)
   cnt = 0
   for m_row in rply_cursor:
       cnt = cnt + 1
       print("Found match",m_row[0])
       m_file.write(m_row[0] + '\n')
   print("DB Count for", icao, " is", cnt)

#get_cosine, text_to_vector from
#https://gist.github.com/ahmetalsan/06596e3f2ea3182e185a
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
   print(words)
   return Counter(words)


#Open database connection and output file
con = lite.connect('adsb.msg')
cur = con.cursor()
print("Successfully Connected to SQLite")
filename = "replay.txt"
myfile = open(filename, 'w')

#This creates a dataset to be used for replay attack
#we will read in the data from the file and dpo 2 things
#first - see if there is a match in data in adsb.flt
#second - create a string that we can use as a vector in cos_sim

#gmrICAO = 'C023B7'
gmrICAO = 'A4D7E4' # this has duplicate msg's
q = "SELECT msg FROM adsb WHERE icao ='" + gmrICAO + "';"

try:
    my_cursor=cur.execute(q)
    
    for row in my_cursor:
        print(row[0])
        myfile.write(row[0] + '\n')
except lite.Error as my_error:
  print("error: ",my_error)

myfile.close()

#I took out a chunk of the records so not an exact match
#Idea being to try to reduce the similarity to taht of
#naturally occuring duplicates
#Next read in the replay text file and find if it has a match
#get a count on number of matches
filename = "replay.txt"
m_name = "match.txt"
myfile = open(filename, 'r')
m_file = open(m_name, 'w')

line = myfile.readline()
cnt = 0
replayICAO = 'Start'
# receive data from the server
#if have rowcount 1 or more, then use icao to get all
#data's that may be related
while(line):
   replay = line[:-1]
   q = "SELECT icao, msg FROM adsb WHERE msg ='" + replay + "';"
   #print(q)
   my_cursor=cur.execute(q)
   rs = my_cursor.fetchall()
   for row in rs:      #need to account for multiple rows for a data val
      if replayICAO != row[0]:
         cnt = cnt + 1
         save_replay(row[0])
         replayICAO = row[0]
         #q = "SELECT data FROM adsb WHERE icao ='" + replayICAO + "';"
         #rply_cursor=cur.execute(q)
         #for m_row in rply_cursor:
         #    print("Found match",m_row[0])
         #    m_file.write(m_row[0] + '\n')
      print(row[0], row[1]) 
      # if multiple rows have different icaos they will go to 
      #save replay - if not then only one went to save_replay
   print(len(rs))
   line = myfile.readline()
   print("Unique ICAO", cnt) #if more than 1 need to account for others
   #to account if more than one, put the select get in a subroutine
   #and each differnet icao will trigger that subroutine
   #get a file of data for each icao
   #cosine on all of them

m_file.close()
myfile.close()
con.close()
filename = "replay.txt"
m_name = "match.txt"
myfile = open(filename, 'r')
m_file = open(m_name, 'r')

line = myfile.readline()
m_line = m_file.readline()
replay = ""
original = ""
while(line):
   replay = replay + line
   line = myfile.readline()

while(m_line):
   original = original + m_line
   m_line = m_file.readline()
    
vector1 = text_to_vector(replay)
vector2 = text_to_vector(original)

cosine = get_cosine(vector1, vector2)

print("Cosine:", cosine)


#next step is to read the two files, replay and match
#make strings of them
#make vecots of strings
#cosine sim on the other

