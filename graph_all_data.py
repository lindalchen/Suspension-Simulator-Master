#################### DESCRIPTION ####################
# This program plots tire data as outputted from 
# 'tire_data_cleaner.py' as .csv files. It generates 
# subplots with relevant information, and produces 
# an interactive graph that is viewable as a web 
# page, and can be exported as a PDF. Look to support
# doc from TTC for variable meaning.
#################### USAGE ##########################
# change file imports (.csv files) in order to plot 
# different data
#####################################################

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="darkgrid")

def plotData(filePath, file, header_length):
	#import data from .csv file
	df = pd.read_csv(filePath+'/'+file, sep=',')
	units = df.iloc[0]
	df = df.drop([0]) # get rid of units row
	print(df.head())

	fig, axes = plt.subplots(nrows=4, ncols=5)
	fig.subplots_adjust(hspace=0.5)
	fig.suptitle('Hoosier 43075, 16.0 x 7.5 - 10, LCO Tire Data')

	for column, title, unit in zip(df, list(df), units): 
		sns.relplot(x='ET', y=column, data=df.astype(float), height=5, aspect=1);
		plt.title('%s [%s] vs. Time [s]' % (title, unit))
		plt.xlabel('Time [s]')
		plt.ylabel('%s [%s]' % (title, unit))

	plt.show()

if __name__ == "__main__":
    filePath = "/Users/Max/Desktop/Personal/School/Princeton/PRE/Suspension-Dynamics-Simulator-master/Xerxes/Python"
    file = 'A1965run18.csv'
    header_length = 2
    plotData(filePath, file, header_length)
