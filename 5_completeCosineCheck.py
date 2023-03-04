"""
This program is the cosine of each ADSB record that was captured
against each of the other 2,127 records (2,128 records total)
The prupose is to find the maximum cosine that results from
natuarrraly occuring duplicates in the ADSB message traffic
A nested loop is setup to loop thru the unioque ICAOs in the traffic table and then for the selected ICAO loop tghrough all the ICAOs and
calculate the cosine. 
A cosine of 1 will occur whejn the outer ICAO is compared to itself
as the ICAO in the inner loop. All other cosines will be the result 
of ntaurally occuring duiplicates
once comapred withj all other ICAOs in the inner loop, that outer loop ICAO is deleted so that its matches are not double counted
the number of computations equals n*(n-1)/2 or for this case
2,128 * 2,127 /2 = 2,263,128
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
   #print(words)
   #print("next words===============")
   return Counter(words)

def compare_all():
   print("Starting compare all")
   #this function assumes the replay message set 
   #is in the replay.txt file 
   #function main should put it there
   myfile = open(filename, 'r')
   line = myfile.readline()
   replay = ""
   while(line):
      replay = replay + line
      line = myfile.readline()
   vector1 = text_to_vector(replay)
   #vector 1 is the replay attack set of messages
   original = ""
   #original is the holder for the set of messages 
   #we get for each ICAO
   #it must be reset each time thru
   q = "SELECT distinct ICAO data FROM adsb;"

   try:
     my_cursor=cur.execute(q)
     results = my_cursor.fetchall()
     for row in results:
        #print("row zero is ", row[0])
        q2 = "SELECT msg from adsb where ICAO = '" + row[0] + "';"
        cur_msg = cur.execute(q2)
        original = ""
        for msg in cur_msg:
           original = original + msg[0] + "\n" #to match file read
        vector2 = text_to_vector(original) 
        cosine = get_cosine(vector1, vector2)
        if cosine > 0: 
           print("This ICAO ", row[0], " has cosine ", cosine, "\n")
           cosFile.write(row[0] + ", " + str(cosine) + '\n')  
           cosFile.flush()  
           os.fsync(cosFile.fileno())  
   except lite.Error as my_error:
     print("error: ",my_error)
   myfile.close()
   print("Leaving compare all")

#Open database connection and output file
con = lite.connect('adsb.msg')
cur = con.cursor()
print("Successfully Connected to SQLite")
filename = "replay.txt"
cosFile = open('cosines.txt', 'a')

#compare_all()

#to do queries
#1. select distinct ICAO from adsb;
#2.  write this to replay file
#3. call compare_all()

q = "SELECT distinct ICAO data FROM adsb limit 100;"
cur2=cur.execute(q)
rs = cur2.fetchall()
for gmrICAO in rs:
   print("starting another ICAO")
   refile = open(filename, 'w')
   q3 = "SELECT msg FROM adsb WHERE icao ='" + gmrICAO[0] + "';"
   try:
     cur3=cur.execute(q3)
     rs3 = cur3.fetchall()
     for r in rs3:
        #print(r[0])
        refile.write(r[0] + '\n')
   except lite.Error as my_error:
     print("error: ",my_error)
   refile.close()
   compare_all()
   print("after comapre all")
   #this may be deadlocked - cannot delete because of read loop
   q4 = "delete from adsb where ICAO = '" + gmrICAO[0] + "';"
   cur4 = cur.execute(q4)
   con.commit()
   print("after delete")
cosFile.close()

