"""
This is a test harness that will eventuall test the following:
1. Write Python program to read tables dups and verify that each of the records in it is present multiple times in table adsb
2. In Python program above, also read table adsb_dup and using msg block read adsb and verify that the ICAO in adsb_dup is in the result set from adsb
3. Same for msg_dups
4.	Read msg_dups and for each msg attribute get the corresponding ICAOs and then using ICAO-msg both read adsb and verify that they are in that table. 
5.	This verifies that different ICAOs can have the same message so cannot just use a find in the database to say it is a replay attack so need to compare blocks of hexadecimal messages 
"""

#Get libraries
import math
import re
from collections import Counter
import sqlite3 as lite

#Open database connection and output file
con = lite.connect('adsb.flt')
cur = con.cursor()
print("Successfully Connected to SQLite")

# have an outer block that loops thru all rcords in msg_dups
#this is one msg (mesage)
#dup = '99917E8158708B'

hold_msg = ''
dup_cnt = 0
qo = "select msg, count(*) from msg_dups group by msg having count(*) > 1;"
my_cursor=cur.execute(qo)
rso = my_cursor.fetchall()
for row in rso:
    dup = row[0]
    q = "SELECT DISTINCT icao FROM adsb WHERE msg ='" + dup + "';"
    my_cursor=cur.execute(q)
    rs = my_cursor.fetchall()
    for row1 in rs:   
       #print(row[0], row[1]) 
       if row[0] != hold_msg:
          print(hold_msg, ": ", dup_cnt)
          hold_msg = row[0]
          dup_cnt = 1
          print(row1[0])
       else:
          print(row1[0])
          dup_cnt = dup_cnt + 1
print(hold_msg, ": ", dup_cnt)

       #add some logic here that control breaks on message (old name data)
       #and counts icao for each message

#print two differnt ICAOs (transponders)had identical messgaes
con.close()
