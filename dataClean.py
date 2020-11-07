#------------------- DESCRIPTION -------------------#
# This Program takes in tire data from TTC as .dat
# files and converts them to csv files
# in order to be utilized in the rest of the
# analysis.
#------------------- USAGE -------------------------#
# change file path and
# names to be imported in main method
# in terminal type: python tire_data_cleaner.py
#---------------------------------------------------#
#------------------- AUTHOR ------------------------#
# @ Xerxes Libsch 5/16/2020
#---------------------------------------------------#

import csv

class dataClean():
    def __init__(self, file_path):
        self.file_path = file_path

    def clean_file(self, fileList, headerPresentList):
        for file, header_present in zip(fileList, headerPresentList):
            with open(self.file_path+'/'+file) as dat_file, open(file[:-4]+'.csv', 'w') as csv_file:
                csv_writer = csv.writer(csv_file)
                first_line = True
                for line in dat_file:
                    if header_present and first_line:
                        first_line = False
                        continue
                    line = line.rstrip()
                    row = [field.strip() for field in line.split('\t')]
                    csv_writer.writerow(row)

if __name__ == "__main__":
    FILE_PATH = "/Users/Max/Desktop/Personal/School/Princeton/PRE/Suspension-Dynamics-Simulator-master/Xerxes/Tire Data/RunData_Cornering_ASCII_USCS_10inch_Round8"
    FILE_LIST = ['A1965run17.dat', 'A1965run18.dat', 'A1965run19.dat']
    HEADERS_PRESENT = [True, True, True]

    cleanClient = dataClean(FILE_PATH)
    cleanClient.clean_file(FILE_LIST, HEADERS_PRESENT)

