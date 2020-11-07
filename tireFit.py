#------------------- DESCRIPTION -------------------# 
# This program estimates the coefficient of friction 
# for a given tire based on camber, slip angle and 
# normal load. It takes a .csv file from TTC data, 
# and outputs a fitting function based on the tire
# data for a given pressure range. In addition, 
# this program generates optimal camber vs. normal 
# force and displacement curves. 
#------------------- USAGE -------------------------#
# instantiate an object and call the appropriate 
# method fitData
#---------------------------------------------------#
#------------------- AUTHOR ------------------------#
# @ Xerxes Libsch 5/16/2020
#---------------------------------------------------#

import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model

from base import base

class tireFit(base):
    def __init__(self, filePath):
        super(tireFit, self).__init__(filePath)

    #----------------------- OPTIMAL CAMBER FUNCTIONS -----------------------
    # returns normal force vs. u function for every top mu out of each discrete bin
    def getMaxMu_OptimalCamber_vs_NormalForce(self, pressureCriteria, binSize):
        filteredData = self.filter_data(self.df, pressureCriteria)
        muSeries = self.get_mu(filteredData)
        filteredData['MU'] = muSeries
        df = filteredData.sort_values('FZ')

        maxMu = []
        normalForce = []
        optimalCambers = []
        binMax = float('-inf')
        normal = 0.0
        camber = 0.0
        # collect the top mu in discrete bins, and get corresponding camber vals
        for index, row in df.iterrows():
            if float(abs(row['MU'])) > binMax:
                binMax = float(row['MU'])
                normal = float(row['FZ'])
                camber = -1.0*float(row['IA'])
            if (index % binSize) == 0:
                maxMu.append(binMax)
                normalForce.append(normal)
                optimalCambers.append(camber)
                binMax = float('-inf')

        return maxMu, optimalCambers, normalForce
    #-------------------- END OPTIMAL CAMBER FUNCTIONS ---------------------

    #------------------------- TIRE FIT FUNCTIONS --------------------------
    # fit [slip angle, camber, normal force] to [mu] using polynomial multiv. regr.
    # returns regression object
    def get_fit_object(self, pressureCriteria):
        filteredData = self.filter_data(self.df, pressureCriteria)
        slipAngles = filteredData['SA'].tolist()
        cambers = list(map(lambda x: -1.0*float(x), filteredData['IA'].tolist()))
        normalForces = filteredData['FZ'].tolist()
        mu = self.get_mu(filteredData).tolist()

        X = []
        for x1, x2, x3 in zip(slipAngles, cambers, normalForces):
            X.append([x1, x2, x3])

        assert(len(X) == len(mu)), "INVALID: Mu and [camber, slipangle, lateral force] lists differ in length"

        poly = PolynomialFeatures(degree=2)
        X_ = poly.fit_transform(X)
        
        clf = linear_model.LinearRegression().fit(X_, mu)
        return clf

    # returns lateral force for a given slip angle, camber and normal force based on fit function
    def get_lateral_force(self, fitObject, slipAngle, camber, normalForce):
        inputs = [float(slipAngle), float(camber), float(normalForce)]
        predict = [inputs]
        poly = PolynomialFeatures(degree=2)
        predict_ = poly.fit_transform(predict)
        cf = fitObject.predict(predict_)
        lateralForce = cf*normalForce
        return lateralForce

    #----------------------- END TIRE FIT FUNCTIONS ------------------------

if __name__ == "__main__":
    #--------------------- Set File Parameters ------------------------
    FILE_PATH = "/Users/Max/Desktop/Personal/School/Princeton/PRE/Suspension-Dynamics-Simulator-master/Xerxes/Python"
    FILE = 'A1965run18.csv'
    fittingClient = tireFit(FILE_PATH+'/'+FILE)
    #------------------- Get Tire Fit Parameters ----------------------
    PRESSURE_CRITERIA = ['P', 9.5, 10.5]
    mus, cambers, normals = fittingClient.getMaxMu_OptimalCamber_vs_NormalForce(PRESSURE_CRITERIA, 200)
    
    fitModel = fittingClient.get_fit_object(PRESSURE_CRITERIA)
    normalForces = [x for x in range(0, 250, 1)]
    lateralForces = []
    slipAngle = 8
    camber = 0
    for x in normalForces:
        latForce = fittingClient.get_lateral_force(fitModel, slipAngle, camber, x)
        lateralForces.append(latForce)
    
    import matplotlib.pyplot as plt
    plt.plot(normalForces, lateralForces)
    plt.title('Lateral Force vs. Normal Force [%f Deg. Slip Angle, %f Deg. Camber]' % (slipAngle,camber))
    plt.xlabel('Normal Force', fontsize=10)
    plt.ylabel('Lateral Force', fontsize=10)
    plt.show()

    normal_fit, optimalCamber_fit = fittingClient.fit_poly(normals, cambers, 3, True)
    #---------- Plot Optimal Camber vs. Normal Force Curve ------------
    d = {'CAM': optimalCamber_fit, 'FZ':normal_fit}
    data = pd.DataFrame(d)
    units = {'FZ': 'Pound', 'CAM': 'Degree'}
    x = {'Column':'FZ', 'Name':'Load'}
    y = {'Column':'CAM', 'Name':'Optimal Camber'}
    filterCriteria = {}
    filterPositive = False
    
    # # empty argument to plot
    # from plot import plot
    # plotClient = plot('')
    # plotClient.plot_data(x, y, filterCriteria, filterPositive, [data, units])