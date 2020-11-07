#------------------- DESCRIPTION -------------------# 
# This program plots tire data as outputted from 
# 'tire_data_cleaner.py' as .csv files. It generates 
# plots based on user input. The user inputs the 
# desired output data, as well as parameters with 
# which the data should be plotted against. For
# example, I want to plot lateral force vs. slip 
# angle with different curves corresponding to 
# different tire pressures. Note that the relevant 
# libraries must be installed in order for the 
# program to work 
#------------------- USAGE -------------------------#
# change file imports (.csv files) in order to plot 
# different data
# set data filter critera in main method
#---------------------------------------------------#
#------------------- AUTHOR ------------------------#
# @ Xerxes Libsch 5/16/2020
#---------------------------------------------------#

import pandas as pd
import plotly
import plotly.graph_objs as go
import numpy as np
from plotly import tools

from base import base

class plot(base):
    def __init__(self, filePath):
        super(plot, self).__init__(filePath)
    #--------------------------- PLOTTING FUNCTIONS ----------------------------
    # plot data, with optional data (as dataFrame) and units(as dictionary) passed to kwargs as list of dictionaries
    def plot_data(self, x, y, filterCriteria, filterPositive, data=[]):
        if not data:
            df = self.df.copy()
            units = self.units.copy()
        else:
            df = data[0] 
            units = data[1]

        # trying to plot mu which is not contained in underlying
        if x['Column'] == 'MU' or y['Column'] == 'MU':
            try:
                muSeries = self.get_mu(df)
                df['MU'] = muSeries
                units['MU'] = 'None'
            except ValueError:
                print('Data insufficient to calculate Mu. Check that data contains \'FY\' and \'FZ\'')
        
        plotData = []

        # plot with filter criteria
        if filterCriteria:
            for key in filterCriteria.keys():
                criteria = filterCriteria[key]
                for regime in criteria:
                    filteredData = self.filter_data(df, [str(key), regime[0], regime[1]])   
                    xData = pd.to_numeric(filteredData[x['Column']])
                    yData = pd.to_numeric(filteredData[y['Column']])
                    if filterPositive:
                        xData, yData = self.get_positive(xData, yData)
                    x_fit, y_fit = self.fit_poly(xData, yData, 2, True)
                    trace = go.Scatter(y=y_fit, x=x_fit, line=dict(width=1), name='%s : [%f-%f]' %(str(key), regime[0], regime[1]))
                    plotData.append(trace)
        
        # otherwise plot normally 
        else: 
            xData = pd.to_numeric(df[x['Column']])
            yData = pd.to_numeric(df[y['Column']])
            if filterPositive:
                xData, yData = self.get_positive(xData, yData)
            x_fit, y_fit = self.fit_poly(xData, yData, 7, True)
            rawData = go.Scatter(y=yData, x=xData, line=dict(width=1))
            fitData = go.Scatter(y=y_fit, x=x_fit, line=dict(width=1))
            plotData.append(rawData)
            plotData.append(fitData)
        
        tit = str("[Hoosier 43075, 16.0 x 7.5 - 10, LCO Tire Data]: %s vs. %s" % (y['Name'], x['Name']))
        xaxisTit = str("%s [%s]" % (x['Name'], units[x['Column']]))
        yaxisTit = str("%s [%s]" % (y['Name'], units[y['Column']]))
        layout = dict(title=tit, 
                xaxis = dict(title = xaxisTit), yaxis = dict(title = yaxisTit))
        fig = dict(data=plotData,layout=layout)

        plotly.offline.plot(fig)
        #------------------------- END PLOTTING FUNCTIONS --------------------------

if __name__ == "__main__":
    #-------------------- Set File Parameters -------------------------
    filePath = "/Users/Max/Desktop/Personal/School/Princeton/PRE/Suspension-Dynamics-Simulator-master/Xerxes/Python/A1965run18.csv"
    #-------------------- Set Graphing Parameters ---------------------
    # # LATERAL FORCE vs. SLIP ANGLE 
    # x = {'Column':'SA', 'Name':'Slip Angle'}
    # y = {'Column':'NFY', 'Name':'Normalized Lateral Force'} #, NORMAL FORCE
    # # filter based on tire pressure regimes. Format: column: [[min1,max1], [min2,max2], ...]
    # filterCriteria = {'P':[[9.5, 10.5], [11.50, 12.50], [13.5,14.5]]}

    # # LOAD vs. LATERAL FORCE
    # x = {'Column':'FZ', 'Name':'Load'}
    # y = {'Column':'FY', 'Name':'Lateral Force'}
    # # filterCriteria = {'P':[[9.5, 10.5], [11.50, 12.50], [13.5,14.5]]}
    # # only want positive lateral force data 
    # filterPositive = True
    # filterCriteria = {}

    # NORMALIZED LATERAL FORCE vs. SLIP ANGLE, NORMAL FORCE
    # x = {'Column':'SA', 'Name':'Slip Angle'}
    # y = {'Column':'NFY', 'Name':'Normalized Lateral Force'}
    # # filter based on tire pressure regimes. Format: column: [[min1,max1], [min2,max2], ...]
    # filterCriteria = {'FZ':[[-275.0, -225.0], [-225.0, -175.0], [-175.0, -125.0], [-110.0, -80], [-65.0, 0]]}

    # # ALIGNING TORQUE vs. SLIP ANGLE, NORMAL FORCE
    # x = {'Column':'SA', 'Name':'Slip Angle'}
    # y = {'Column':'MZ', 'Name':'Aligning Torque'}
    # # filter based on tire pressure regimes. Format: column: [[min1,max1], [min2,max2], ...]
    # filterPositive = False
    # filterCriteria = {'FZ':[[-275.0, -225.0], [-225.0, -175.0], [-175.0, -125.0], [-110.0, -80], [-65.0, 0]]}

    # # LATERAL FORCE vs. SLIP ANGLE, CAMBER
    # x = {'Column':'SA', 'Name':'Slip Angle'}
    # y = {'Column':'FY', 'Name':'Lateral Force'}
    # # filter based on tire pressure regimes. Format: column: [[min1,max1], [min2,max2], ...]
    # filterCriteria = {'IA':[[-0.5, 0.5], [1.5, 2.5], [3.5, 4.5]]}
    # filterPositive = False

    # # MU vs. LOAD
    # x = {'Column':'FZ', 'Name':'Load'}
    # y = {'Column':'MU', 'Name':'Mu'}
    # filterCriteria = {'IA':[[-0.5, 0.5], [1.5, 2.5], [3.5, 4.5]]}
    # # only want positive lateral force data 
    # filterPositive = True

    #-------------------- Generate Plots ------------------------------
    plotClient = plot(filePath)
    plotClient.plot_data(x, y, filterCriteria, filterPositive)
