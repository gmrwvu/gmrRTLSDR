import pyModeS as pms
import sqlite3 as lite

#Open database connection
con = lite.connect('adsb.msg')
cur = con.cursor()
print("Successfully Connected to SQLite")

#test connection with a read to standard sqlite3 dictionary
sql_query = """SELECT name FROM sqlite_master  
  WHERE type='table';"""
cur.execute(sql_query)
print(cur.fetchall())

# Open data file
filename = "adsb_data_new.txt"
myfile = open(filename, 'r')
line = myfile.readline()

cnt = 1
# input data to the server 
while(line):
  df_cap = line[:2]
  #we only want civilian ADS-B not all Mode-S traffic
  if pms.df(line) in [17,18]:
   #don't need surface position;
   #aircraft status will be multiple dups 
   #collect only 9-22 
   #NEED TO CHECK IF ONLY STATUS MESSAGES 
   #ARE BEING SENT (28-31)
   #OR IF RESERVED TYPES BEING USED (23-27)
   if pms.typecode(line) in range(9, 23): 
     #print(pms.df(line),pms.icao(line), line)
     icao = line[2:8]
     msg = line[8:22]
     crc = line[-6:]
     #print("DF-cap",df_cap)
     qry = "INSERT INTO adsb (dfcap, icao, msg, crc, raw) "
     qry = qry + "VALUES ('" + df_cap + "', '" + icao + "', '" 
     qry = qry + msg + "', '" + crc + "', '" + line + "')"
     #print(qry)
     count = cur.execute(qry)     
     #print("icao", icao, " msg", msg)
     #print("raw", line)
     #print("-----------------------------------------------")

     cnt = cnt + 1
  line = myfile.readline()
  #if cnt > 1000:
  #  break 

print("Count",cnt)
con.commit()

#5,474,723
