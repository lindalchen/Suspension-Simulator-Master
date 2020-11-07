#################### DESCRIPTION ####################
# This Program takes in tire data from TTC as .dat 
# files and converts them to csv files 
# in order to be utilized in the rest of the 
# analysis.
#################### USAGE ##########################
# change file path and 
# names to be imported in main method
# in terminal type: python tire_data_cleaner.py
#####################################################

import numpy as np
import csv

class dataClean():
    def __init__(self, filePath): 

def dataClean(filePath, fileList, header_present):
    for file in fileList:
        with open(filePath+'/'+file) as dat_file, open(file[:-4]+'.csv', 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            firstLine = True 
            for line in dat_file:
                if header_present is True and firstLine == True:
                    firstLine = False 
                    continue
                line = line.rstrip()
                print(line.split('\t'))
                row = [field.strip() for field in line.split('\t')]
                csv_writer.writerow(row)

if __name__ == "__main__":
    filePath = "/Users/Max/Desktop/Personal/School/Princeton/PRE/Suspension-Dynamics-Simulator-master/Xerxes/Tire Data/RunData_Cornering_ASCII_USCS_10inch_Round8"
    fileList = ['A1965run17.dat', 'A1965run18.dat', 'A1965run19.dat']
    header_present = True
    dataClean(filePath, fileList, header_present)

