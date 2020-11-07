#------------------- DESCRIPTION -------------------# 
# This program generates suspension
# geometry based on tire data. Tire data is analyzed 
# by tireFit.py, which outputs an optimal camber vs. 
# force curve. 
#------------------- USAGE -------------------------#
# instantiate an object and call the appropriate 
# methods 
#---------------------------------------------------#

from __future__ import division

from base import base
from tireFit import tireFit

class geometry(base):
    def __init__(self):
        pass

    #--------------------------- CAMBER ----------------------------
    # returns resting camber based on resting force. 
    def getOptimalRestingCamber(self, normalForceList, optimalCamberList, restingForce):
        assert (restingForce <= max(normalForceList) and restingForce >= min(normalForceList)), "INVALID: Resting Force outside force range"
        assert(len(normalForceList) == len(optimalCamberList)), "INVALID: Lists differ in length"
        
        normalForceList, optimalCamberList = (list(t) for t in zip(*sorted(zip(normalForceList, optimalCamberList))))
        count = 0
        while(count < len(optimalCamberList)-1):
            if normalForceList[count] <= restingForce and normalForceList[count+1] >= restingForce:
                return (optimalCamberList[count]+optimalCamberList[count+1])/float(2)       
            count = count+1

    # returns average wheel displacement for range of normal forces FZ. Wheel rate in lb/in (K)
    def getOptimalCamberVsDisplacement(self, wheelRate, FZmin, FZmax, normalForceList, optimalCamberList):
        assert (FZmin < FZmax),"INVALID: Maximum force is smaller than minimum force!"
        assert(len(normalForceList) == len(optimalCamberList)), "INVALID: Lists differ in length"
        
        displacements = []
        optimalCambers = []

        for force, camber in zip(normalForceList, optimalCamberList):
            if force <= FZmax and force >= FZmin:
                displacement = -1*abs(float(force)/float(wheelRate))
                displacements.append(displacement)
                optimalCambers.append(camber)

        return displacements, optimalCambers

    # return average camber gain versus displacements. Camber gain negative for increasing (more negative) camber from rest.
    def getOptimalCamberGainVsDisplacement(self, displacements, optimalCambers, restingCamber):
        assert (restingCamber < max(optimalCambers) and restingCamber > min(optimalCambers)), "INVALID: Resting camber outside camber range"
        assert(len(displacements) == len(optimalCambers)), "INVALID: Lists differ in length"

        return list(map(lambda x: x-restingCamber, optimalCambers)), displacements

    # returns average camber gain 
    def getAverageCamberGain(self, camberList):
        return sum(camberList)/float(len(camberList))
    #-------------------------- END CAMBER ----------------------------

if __name__ == "__main__":
    #--------------------- Set File Parameters ------------------------
    filePath = "/Users/Max/Desktop/Personal/School/Princeton/PRE/Suspension-Dynamics-Simulator-master/Xerxes/Python"
    file = 'A1965run18.csv'
    tireClient = tireFit(filePath+'/'+file)
    #------------------- Get Tire Fit Parameters ----------------------
    pressureCriteria = ['P', 9.5, 10.5]
    mus, cambers, normals = tireClient.getMaxMu_OptimalCamber_vs_NormalForce(pressureCriteria, 200)
    normal_fit, optimalCamber_fit = tireClient.fitPoly(normals, cambers, 3, True)
    #------------- Get Optimal Suspension Fit Parameters --------------
    wheelRate = 150  #lb/in
    FZmin = -260     #lb
    FZmax = -40      #lb
    geometryClient = geometry()
    displacements, optimalCambers = geometryClient.getOptimalCamberVsDisplacement(wheelRate, 
            FZmin, FZmax, normal_fit, optimalCamber_fit)
    
    restingForce = -100 #lb
    restingCamber = geometryClient.getOptimalRestingCamber(normal_fit, optimalCamber_fit, restingForce)
    camberGains, displacements = geometryClient.getOptimalCamberGainVsDisplacement(displacements, 
            optimalCambers, restingCamber)
    #------------------------- Plot Curves -----------------------------
    import pandas as pd
    from plot import plot 
    
    d = {'CAM': optimalCambers, 'DIS':displacements}
    data = pd.DataFrame(d)
    units = {'CAM': 'Degree', 'DIS': 'Inches'}
    x = {'Column':'DIS', 'Name':'Displacement From Rest'}
    y = {'Column':'CAM', 'Name':'Optimal Camber'}
    filterCriteria = {}
    filterPositive = False

    # empty argument to plot
    plotClient = plot('')
    plotClient.plotData(x, y, filterCriteria, filterPositive, [data, units])

    # d2 = {'delCAM': camberGains, 'DIS':displacements}
    # data2 = pd.DataFrame(d2)
    # units2 = {'delCAM': 'Degree', 'DIS': 'Inches'}
    # x2 = {'Column':'DIS', 'Name':'Displacement From Rest'}
    # y2 = {'Column':'delCAM', 'Name':'Optimal Camber Gain'}
    # filterCriteria2 = {}
    # filterPositive2 = False

    # # empty argument to plot
    # plotClient2 = plot('')
    # plotClient2.plotData(x2, y2, filterCriteria2, filterPositive2, [data2, units2])





