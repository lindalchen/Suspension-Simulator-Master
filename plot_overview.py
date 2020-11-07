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

	trace1 = go.Scatter(y=df['AmbTmp'], x=df['ET'], line = dict(width=0.5), mode='markers')
	trace2 = go.Scatter(y=df['FX'], x=df['ET'], line = dict(width=1), mode='markers')
	trace3 = go.Scatter(y=df['FY'], x=df['ET'], line = dict(width=1), mode='markers')
	trace4 = go.Scatter(y=df['FZ'], x=df['ET'],  line = dict(width=1), mode='markers')
	trace5 = go.Scatter(y=df['IA'], x=df['ET'], line = dict(width=0.5), mode='markers')
	trace6 = go.Scatter(y=df['MX'], x=df['ET'], line = dict(width=1), mode='markers')
	trace7 = go.Scatter(y=df['MZ'], x=df['ET'], line = dict(width=1), mode='markers')
	trace8 = go.Scatter(y=df['N'], x=df['ET'],  line = dict(width=1), mode='markers')
	trace9 = go.Scatter(y=df['NFX'], x=df['ET'], line = dict(width=0.5), mode='markers')
	trace10 = go.Scatter(y=df['NFY'], x=df['ET'], line = dict(width=1), mode='markers')
	trace11 = go.Scatter(y=df['P'], x=df['ET'], line = dict(width=1), mode='markers')
	trace12 = go.Scatter(y=df['RE'], x=df['ET'],  line = dict(width=1), mode='markers')
	trace13 = go.Scatter(y=df['RL'], x=df['ET'], line = dict(width=0.5), mode='markers')
	trace14 = go.Scatter(y=df['RST'], x=df['ET'], line = dict(width=1), mode='markers')
	trace15 = go.Scatter(y=df['SA'], x=df['ET'], line = dict(width=1), mode='markers')
	trace16 = go.Scatter(y=df['SR'], x=df['ET'],  line = dict(width=1), mode='markers')
	trace17 = go.Scatter(y=df['TSTC'], x=df['ET'], line = dict(width=0.5), mode='markers')
	trace18 = go.Scatter(y=df['TSTI'], x=df['ET'], line = dict(width=1), mode='markers')
	trace19 = go.Scatter(y=df['TSTO'], x=df['ET'], line = dict(width=1), mode='markers')
	trace20 = go.Scatter(y=df['V'], x=df['ET'], line = dict(width=1), mode='markers')

	fig = tools.make_subplots(rows=10, cols=2, subplot_titles=('Ambient Room Temperature vs. Time', 
			'Longitudinal Force vs. Time, Lateral Force vs. Time', 'Normal Load vs. Time',
			'Inclination Angle vs. Time', 'Overturning Moment vs. Time', 'Aligning Torque vs. Time', 
			'Wheel Rotation Speed vs Time', 'Normalized Longitudinal Force vs. Time', 
			'Normalized Lateral Force vs. Time', 'Tire Pressure vs. Time', 'Effective Radius vs. Time',
			'Loaded Radius vs. Time', 'Road Surface Temperature vs. Time', 'Slip Ratio vs. Time', 
			'Tire Surface Temp -- Center vs. Time', 'Tire Surface Temp -- Inboard vs. Time', 
			'Tire Surface Temp -- Outboard vs. Time', 'Road Speed vs. Time'))

	fig.append_trace(trace1, 1, 1)
	fig.append_trace(trace2, 1, 2)
	fig.append_trace(trace3, 2, 1)
	fig.append_trace(trace4, 2, 2)
	fig.append_trace(trace5, 3, 1)
	fig.append_trace(trace6, 3, 2)
	fig.append_trace(trace7, 4, 1)
	fig.append_trace(trace8, 4, 2)
	fig.append_trace(trace9, 5, 1)
	fig.append_trace(trace10, 5, 2)
	fig.append_trace(trace11, 6, 1)
	fig.append_trace(trace12, 6, 2)
	fig.append_trace(trace13, 7, 1)
	fig.append_trace(trace14, 7, 2)
	fig.append_trace(trace15, 8, 1)
	fig.append_trace(trace16, 8, 2)
	fig.append_trace(trace17, 9, 1)
	fig.append_trace(trace18, 9, 2)
	fig.append_trace(trace19, 10, 1)
	fig.append_trace(trace20, 10, 2)

	# fig['layout']['xaxis1'].update(title='Slip Angle (deg)')
	# fig['layout']['xaxis2'].update(title='Slip Ratio (SAE-convention)')
	# fig['layout']['xaxis3'].update(title='Normal Load (lb)')
	# fig['layout']['xaxis4'].update(title='Pressure (psi)')

	# fig['layout']['yaxis1'].update(title='Lateral Force (lb)')
	# fig['layout']['yaxis2'].update(title='Longitudinal Force (lb)')
	# fig['layout']['yaxis3'].update(title='Lateral Force (lb)')
	# fig['layout']['yaxis4'].update(title='Lateral Force (lb)')

	fig['layout'].update(title='Hoosier 43075, 16.0 x 7.5 - 10, LCO Tire Data')

	plotly.offline.plot(fig)

if __name__ == "__main__":
    filePath = "/Users/Max/Desktop/Personal/School/Princeton/PRE/Suspension-Dynamics-Simulator-master/Xerxes/Python"
    file = 'A1965run18.csv'
    header_length = 2
    plotData(filePath, file, header_length)



