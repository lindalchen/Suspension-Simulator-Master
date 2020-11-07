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

	lateralForce = pd.to_numeric(df['NFY'])
	slipAngle = pd.to_numeric(df['SA'])
	# calculate polynomial fit
	z = np.polyfit(slipAngle, lateralForce, 10)
	f = np.poly1d(z)

	y_fit = map(f,slipAngle) # invert curve
	trace1 = go.Scatter(y=y_fit, x=slipAngle, line=dict(width=1))

	# plot data 
	data = [trace1]
	layout = dict(title="Hoosier 43075, 16.0 x 7.5 - 10, LCO Tire Data Lateral Force vs. Slip Angle", xaxis = dict(title = 'Slip Angle (deg)'),
	             yaxis = dict(title = ' Normalized Lateral Force (lb)'))
	fig = dict(data=data,layout=layout)
	plotly.offline.plot(fig)

if __name__ == "__main__":
    filePath = "/Users/Max/Desktop/Personal/School/Princeton/PRE/Suspension-Dynamics-Simulator-master/Xerxes/Python"
    file = 'A1965run19.csv'
    header_length = 2
    plotData(filePath, file, header_length)