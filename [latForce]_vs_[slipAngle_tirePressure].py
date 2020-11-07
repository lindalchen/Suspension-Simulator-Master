#################### DESCRIPTION ####################
# This program plots tire data as outputted from 
# 'tire_data_cleaner.py' as .csv files. It generates 
# plots based on user input. The user inputs the 
# desired output data, as well as parameters with 
# which the data should be plotted against. For
# example, I want to plot lateral force vs. slip 
# angle with different curves corresponding to 
# different tire pressures. 
#################### USAGE ##########################
# change file imports (.csv files) in order to plot 
# different data
# set data filter critera
#####################################################

import pandas as pd
import plotly
import plotly.graph_objs as go
import numpy as np
from plotly import tools

def plotData(filePath, file, header_length):
	#import data from .csv file 
	df = pd.read_csv(filePath+'/'+file, sep=',')
	df = df.drop([0]) # get rid of units header
	print(df.head())

	# filter based on tire pressure regimes. Format: column: [[min1,max1], [min2,max2], ...]
	filterCriteria = {'P':[[9.5, 10.5], [11.5,12.5], [13.5,14.5]]}
	
	# generate different trace for each filter criteria
	plotData = []
	for key in filterCriteria.keys():
		criteria = filterCriteria[key]
		for regime in criteria:
			filteredData = filterData(df, str(key), regime[0], regime[1])
			lateralForce = pd.to_numeric(filteredData['NFY'])
			slipAngle = pd.to_numeric(filteredData['SA'])
			# calculate polynomial fit
			try: 
				z = np.polyfit(slipAngle, lateralForce, 10)
				f = np.poly1d(z)
			except:
				print('Regime value specified is outside of data range. No data available for this range.')
			y_fit = map(f,slipAngle)

			trace = go.Scatter(y=y_fit, x=slipAngle, line=dict(width=1), name='%s : [%f-%f]' %(str(key), regime[0], regime[1]))
			plotData.append(trace)

	# plot data
	layout = dict(title="Hoosier 43075, 16.0 x 7.5 - 10, LCO Tire Data Lateral Force vs. Slip Angle as a Function of Pressure", xaxis = dict(title = 'Slip Angle (deg)'),
	             yaxis = dict(title = ' Normalized Lateral Force (lb)'))
	fig = dict(data=plotData,layout=layout)
	plotly.offline.plot(fig)

def filterData(dataFrame, filterColumn, min, max):
	return dataFrame.loc[(dataFrame[filterColumn] >= min) & (dataFrame[filterColumn] <= max)]

if __name__ == "__main__":
	#-------------------- Set File Parameters -------------------------
    filePath = "/Users/Max/Desktop/Personal/School/Princeton/PRE/Suspension-Dynamics-Simulator-master/Xerxes/Python"
    file = 'A1965run18.csv'
    header_length = 2
    #-------------------- Set Graphing Parameters ---------------------
    outputData = {}
    plotData(filePath, file, header_length)







