#------------------- DESCRIPTION -------------------#
# This program implements base functionality for
# suspension and tire sub-classes.
#------------------- USAGE -------------------------#
# Utilize inhertiance to implement functionality
# contained herein
#---------------------------------------------------#
#------------------- AUTHOR ------------------------#
# @ Xerxes Libsch 5/16/2020
#---------------------------------------------------#
import csv
import pandas as pd
import numpy as np

class base(object):
    def __init__(self, filePath=''):
        if not filePath:
            self.df = pd.DataFrame(data={})
            self.units = {}
        
        else:
            self.df = pd.read_csv(filePath, sep=',')
            self.units = {}

            if isinstance(self.df.iloc[1][0], str): # save and get rid of units header if we have one
                for unit, column in zip(self.df.iloc[0], list(self.df)):
                    self.units[column] = unit
            self.df = self.df.drop([0])
            self.df = self.df.apply(pd.to_numeric, errors='coerce') # added code by linda

    #---------------------------  BASE DATA OPERATIONS ----------------------------
    # filter df based on min max criteria for data in a column
    def filter_data(self, df, filterCriteria):
        filterColumn = filterCriteria[0]
        minimum = filterCriteria[1]
        maximum = filterCriteria[2]
        df[filterColumn] = df[filterColumn].astype(float)
        return df.loc[(df[filterColumn] >= minimum) & (df[filterColumn] <= maximum)]

    # return linear data range between min and max of series
    def get_linear_range(self, series, rangeCrit=[]):
        if not rangeCrit:
            return np.linspace(min(series), max(series), (max(series)-min(series))*100)
        return np.linspace(rangeCrit[0], rangeCrit[1], rangeCrit[2])

    # return x and y data only corresponding to positive y
    def get_positive(self, x, y):
        count = 0
        temp = []
        for num in x:
            if y.iloc[count] >= 0:
                temp.append(x.iloc[count])
            count += 1
        x = pd.Series(temp)
        y = y[y>=0]
        return x, y

    # polynomial fit. rangeCrit --> [min, max, numberSteps] normals, cambers, 3, True, [0,2,2000])
    def fit_poly(self, x, y, polynomialOrder=10, interpolate=False, rangeCrit=[]):
        z = np.polyfit(x, y, polynomialOrder)
        f = np.poly1d(z)

        if interpolate:
            if not rangeCrit:
                x_interp = self.get_linear_range(x)
            else:
                x_interp = self.get_linear_range(x, rangeCrit)
            y_interp = map(f, x_interp)
            return x_interp, y_interp

        else:
            y_fit = map(f, x)
            return x, y_fit

    # calculate mu
    def get_mu(self, df):
        try:
            muSeries = df['FY'].astype(float)/df['FZ'].astype(float)
        except ValueError:
            print ('Data not in correct format. Check that data has FY and FZ columns of equal length.')
        return muSeries
    #--------------------------- END BASE DATA OPERATIONS ----------------------------

    #-------------------------- CSV FILE CONFIG OPERATIONS ---------------------------
    # get order mapping of indices in tuple to dictionary 
    def get_order_mapping(self):
        # order of variables within optimizing tuple output 
        orderDict = {0:'FTFC', 1:'FTRC', 2:'FBFC', 3:'FBRC', 4:'FUK', 
        5:'FLK', 6:'FTCP', 7:'RTFC', 8:'RTRC', 9:'RBFC', 10:'RBRC', 
        11:'RUK', 12:'RLK', 13:'RTCP', 14:'FCO', 15:'RCO'}
        return orderDict

    # map Name to Position
    def get_name_position_map(self):
        nameMap = {'Front top forward chassis pickup':0, 'Front top rearward chassis pickup':1, 'Front bottom forward chassis pickup':2, 
                    'Front bottom rearward chassis pickup':3, 'Front upper kingpin pickup':4, 'Front lower kingpin pickup':5, 
                    'Front tire contact patch':6, 'Rear top forward chassis pickup':7, 'Rear top rearward chassis pickup':8, 
                    'Rear bottom forward chassis pickup':9, 'Rear bottom rearward chassis pickup':10, 'Rear upper kingpin pickup':11, 
                    'Rear lower kingpin pickup':12,'Rear tire contact patch':13, 'Front camber offset relative to kingpin':14, 
                    'Rear camber offset relative to kingpin':15}
        return nameMap

    # read constants for transient response calculations
    def read_transient_csv(self, file):
        pointDict = {}
        with open(file) as csvfile:
            csvfile = csv.reader(csvfile, delimiter=',')
            for row in csvfile:
                if (row[0] == 'Front toe'):
                    pointDict['FT'] = float(row[1])
                elif (row[0] == 'Front tire spring rate'):
                    pointDict['FTSR'] = float(row[1])
                elif (row[0] == 'Front shock spring rate'):
                    pointDict['FSSR'] = float(row[1])
                elif (row[0] == 'Front motion ratio'):
                    pointDict['FMR'] = float(row[1])
                elif (row[0] == 'Front anti-roll stiffness'):
                    pointDict['FARS'] = float(row[1])
                elif (row[0] == 'Front damping ratio'):
                    pointDict['FDR'] = float(row[1])
                elif (row[0] == 'Front corner unsprung mass'):
                    pointDict['FUM'] = float(row[1])
                elif (row[0] == 'Front corner sprung mass'):
                    pointDict['FSM'] = float(row[1])
                elif (row[0] == 'Rear toe'):
                    pointDict['RT'] = float(row[1])
                elif (row[0] == 'Rear tire spring rate'):
                    pointDict['RTSR'] = float(row[1])
                elif (row[0] == 'Rear shock spring rate'):
                    pointDict['RSSR'] = float(row[1])
                elif (row[0] == 'Rear motion ratio'):
                    pointDict['RMR'] = float(row[1])
                elif (row[0] == 'Rear anti-roll stiffness'):
                    pointDict['RARS'] = float(row[1])
                elif (row[0] == 'Rear damping ratio'):
                    pointDict['RDR'] = float(row[1])
                elif (row[0] == 'Rear corner unsprung mass'):
                    pointDict['RUM'] = float(row[1])
                elif (row[0] == 'Rear corner sprung mass'):
                    pointDict['RSM'] = float(row[1])
                elif (row[0] == 'Center of gravity height'):
                    pointDict['COG'] = float(row[1])
                elif (row[0] == 'Polar moment of inertia about COG z-axis'):
                    pointDict['PMOI'] = float(row[1])
                elif (row[0] == 'Front tire contact patch'):
                    pointDict['FTCP'] = [float(row[1]), float(row[2]), float(row[3])]
                elif (row[0] == 'Rear tire contact patch'):
                    pointDict['RTCP'] = [float(row[1]), float(row[2]), float(row[3])]

        if (len(pointDict) < 20):
            raise ValueError('ERROR: Suspension points file does not have all required points. Check that point names haven\'t been changed or have spaces added to end.')
        
        print('Suspension values read:')
        for key in pointDict:
            print (key + ':     ' + str(pointDict[key]))

        return pointDict
        
    # read suspension file
    def read_suspension_csv(self, file):
        pointDict = {}
        with open(file) as csvfile:
            csvfile = csv.reader(csvfile, delimiter=',')
            for row in csvfile:
                if row[0] == 'Front top forward chassis pickup':
                    pointDict['FTFC'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Front top rearward chassis pickup':
                    pointDict['FTRC'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Front bottom forward chassis pickup':
                    pointDict['FBFC'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Front bottom rearward chassis pickup':
                    pointDict['FBRC'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Front upper kingpin pickup':
                    pointDict['FUK'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Front lower kingpin pickup':
                    pointDict['FLK'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Front tire contact patch':
                    pointDict['FTCP'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Rear top forward chassis pickup':
                    pointDict['RTFC'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Rear top rearward chassis pickup':
                    pointDict['RTRC'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Rear bottom forward chassis pickup':
                    pointDict['RBFC'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Rear bottom rearward chassis pickup':
                    pointDict['RBRC'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Rear upper kingpin pickup':
                    pointDict['RUK'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Rear lower kingpin pickup':
                    pointDict['RLK'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Rear tire contact patch':
                    pointDict['RTCP'] = [float(row[1]), float(row[2]), float(row[3])]
                elif row[0] == 'Front camber offset relative to kingpin':
                    pointDict['FCO'] = [float(row[1])]
                elif row[0] == 'Rear camber offset relative to kingpin':
                    pointDict['RCO'] = [float(row[1])]

        if (len(pointDict) < 16):
            raise ValueError('ERROR: Suspension points file does not have all required points. Check that point names haven\'t been changed or have spaces added to end.')

        return pointDict

    #------------------------  END CSV FILE CONFIG OPERATIONS -------------------------

