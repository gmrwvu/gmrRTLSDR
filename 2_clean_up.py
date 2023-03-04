"""
rtlsdr routine adds * at beginning and has crlf at end, 
must clean data before processing
tellLine is the cleaned data that is raw ADS-B message
pms.tell give complete parse of message, not needed for this exercise
"""

import sys
import pyModeS as pms

#This file is the results of using rtlsdr
filename = "adbs_data_in.txt"
myfile = open(filename, 'r')

filename = "adbs_data_new.txt"
outfile = open(filename, 'w')

gmrLines = myfile.readlines()
for s in gmrLines:
    #cleanup crlf, ";" and * from the conversion to Mode S
    gmrLine = s[1:len(s)]
    tellLine = gmrLine.replace(";","")
    outfile.write(tellLine)
    #df = pms.df(tellLine)
    #icao = ""
    #msgType = ""
    #print("df",pms.df(tellLine))
    #if df not in [0,4,5,16,20]:
      #icao = pms.icao(tellLine)
      #print("icao",pms.icao(tellLine))
      #msgType = pms.typecode(tellLine)
      #print("Msg Type", pms.typecode(tellLine))
      #pms.tell(tellLine)

outfile.close()

