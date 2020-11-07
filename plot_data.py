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
# in terminal type: python tire_data_cleaner.py
#####################################################

import pandas as pd
import plotly
import plotly.graph_objs as go
import numpy as np
from plotly import tools

def plotData(filePath, file, header_length):
	#import data from .csv file outputted by 
	df = pd.read_csv(filePath+'/'+file, sep=',')
	df = df.drop([0]) # get rid of units header
	print(df.head())

	trace1 = go.Scatter(y=df['FY'], x=df['SA'], line = dict(width=0.5), mode='markers')
	trace2 = go.Scatter(y=df['FX'], x=df['SR'], line = dict(width=0.5), mode='markers')
	trace3 = go.Scatter(y=df['FY'], x=df['FZ'], line = dict(width=0.5), mode='markers')
	trace4 = go.Scatter(y=df['FY'], x=df['P'],  line = dict(width=0.5), mode='markers')

	fig = tools.make_subplots(rows=2, cols=2, subplot_titles=('Lateral Force vs. Slip Angle', 'Longitudinal Force vs. Slip Ratio',
	                                                          'Lateral Force vs. Normal Load', 'Lateral Force vs. Pressure'))
	fig.append_trace(trace1, 1, 1)
	fig.append_trace(trace2, 1, 2)
	fig.append_trace(trace3, 2, 1)
	fig.append_trace(trace4, 2, 2)

	fig['layout']['xaxis1'].update(title='Slip Angle (deg)')
	fig['layout']['xaxis2'].update(title='Slip Ratio (SAE-convention)')
	fig['layout']['xaxis3'].update(title='Normal Load (lb)')
	fig['layout']['xaxis4'].update(title='Pressure (psi)')

	fig['layout']['yaxis1'].update(title='Lateral Force (lb)')
	fig['layout']['yaxis2'].update(title='Longitudinal Force (lb)')
	fig['layout']['yaxis3'].update(title='Lateral Force (lb)')
	fig['layout']['yaxis4'].update(title='Lateral Force (lb)')

	fig['layout'].update(title='Hoosier 43075, 16.0 x 7.5 - 10, LCO Tire Data')

	plotly.offline.plot(fig)

if __name__ == "__main__":
    filePath = "/Users/Max/Desktop/Personal/School/Princeton/PRE/Suspension-Dynamics-Simulator-master/Xerxes/Python"
    file = 'A1965run18.csv'
    header_length = 2
    plotData(filePath, file, header_length)



