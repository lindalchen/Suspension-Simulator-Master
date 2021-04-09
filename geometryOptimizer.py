#------------------- DESCRIPTION -------------------# 
# This program generates suspension
# geometry based on tire data. Tire data is analyzed 
# by tireFit.py, which outputs an optimal camber vs. 
# force curve. 
#------------------- USAGE -------------------------#
# instantiate an object and call the appropriate 
# methods 
#---------------------------------------------------#
#------------------- AUTHOR ------------------------#
# @ Xerxes Libsch 5/16/2020
#---------------------------------------------------#

from __future__ import division

from base import base #hello this is my comment
from tireFit import tireFit
from optimize import optimize
from kinematics import kinematics 

class geometryOptimizer(optimize):
    def __init__(self):
        pass

    #--------------------------- CAMBER FUNCTIONS ----------------------------
    # returns resting camber based on static resting force on car
    # this function is not used lol
    def get_optimal_resting_camber(self, normalForceList, optimalCamberList, restingForce):
        assert (restingForce <= max(normalForceList) and restingForce >= min(normalForceList)), "INVALID: Resting Force outside force range"
        assert(len(normalForceList) == len(optimalCamberList)), "INVALID: Lists differ in length"
        
        normalForceList, optimalCamberList = (list(t) for t in zip(*sorted(zip(normalForceList, optimalCamberList))))
        count = 0
        while(count < len(optimalCamberList)-1):
            if normalForceList[count] <= restingForce and normalForceList[count+1] >= restingForce:
                return (optimalCamberList[count]+optimalCamberList[count+1])/float(2)       
            count = count+1

    # returns average wheel displacement for range of normal forces FZ. Wheel rate in lb/in (K)
    def get_optimal_camber_displacement_curve(self, wheelRate, FZmin, FZmax, normalForceList, optimalCamberList):
        assert (FZmin < FZmax),"INVALID: Maximum force is smaller than minimum force!"
        assert(len(normalForceList) == len(optimalCamberList)), "INVALID: Lists differ in length"
        
        displacements = []
        optimalCambers = []

        for force, camber in zip(normalForceList, optimalCamberList):
            if force <= FZmax and force >= FZmin:
                displacement = abs(float(force)/float(wheelRate))
                displacements.append(displacement)
                optimalCambers.append(camber)

        return displacements, optimalCambers

    # return average camber gain versus displacements. Camber gain negative for increasing (more negative) camber from rest.
    # this is also not being used in the code
    # relative change in camber so (camber at load - resting camber) and taking the average of that
    def get_optimal_camberGain_displacement_curve(self, displacements, optimalCambers, restingCamber):
        assert (restingCamber < max(optimalCambers) and restingCamber > min(optimalCambers)), "INVALID: Resting camber outside camber range"
        assert(len(displacements) == len(optimalCambers)), "INVALID: Lists differ in length"

        return displacements, list(map(lambda x: x-restingCamber, optimalCambers))

    # returns average camber gain
    # this is just average camber gain, but we don't know with respect to what forces
    # i think the code above it is better?
    def get_average_camber_gain(self, camberList):
        return sum(camberList)/float(len(camberList))

    # get physical camber vs. displacement curve
    def get_real_camber_displacement_curve(self, suspensionCSVFilePath, zRange, deltaZ):
        kinematicsObj = kinematics()
        front, rear = kinematicsObj.main(suspensionCSVFilePath, zRange, deltaZ)
        frontDisplacements = front[0]
        frontCamber = front[1]
        rearDisplacements = rear[0]
        rearCamber = rear[1]

        return frontDisplacements, frontCamber, rearDisplacements, rearCamber
    #-------------------------- END CAMBER FUNCTIONS ---------------------------

    #--------------------------  OPTIMIZE FUNCTIONS ----------------------------
    # get bounds tuple for constrained optimization 
    def get_bounds(self, suspensionCSVFilePath):
        boundsList = self.get_bounds_list(suspensionCSVFilePath)
        return tuple(boundsList)

    # get initial parameter guess for constrained optimization 
    def get_initial_param_list(self, suspensionCSVFilePath):
        paramList = self.get_initial_param_guess(suspensionCSVFilePath)
        return tuple(paramList)

    # optimize geometry based on tire data and suspension parameters
    def get_optimal_geometry(self, tireDataPath , suspensionCSVFilePath, tirePressureCriteria,
            FZmin, FZmax, wheelRate, numIterations, front_or_rear):
        # get optimal mu-camber curve based on tire data
        tireClient = tireFit(tireDataPath)
        mus, cambers, normals = tireClient.getMaxMu_OptimalCamber_vs_NormalForce(tirePressureCriteria, 200)
        # produces the fitted polynomial points of the camber curve with respect to normal
        # normal_fit is a ndarray with info about it and the array, while optimialCamber_fit is an array
        normal_fit, optimalCamber_fit = tireClient.fit_poly(normals, cambers, 3, True, [FZmin,FZmax, abs(FZmin-FZmax)*100])

        # get displacement camber curve
        displacements, optimalCambers = self.get_optimal_camber_displacement_curve(wheelRate, 
            FZmin, FZmax, normal_fit, optimalCamber_fit)

        bounds = self.get_bounds(suspensionCSVFilePath)
        startingVals = self.get_initial_param_list(suspensionCSVFilePath) 
        zRange = max(displacements) - min(displacements)
        deltaZ = zRange/len(displacements)

        # optimize geometry is in optimize.py
        suspensionPoints = self.optimize_geometry(optimalCambers, displacements, suspensionCSVFilePath, zRange,
            deltaZ, startingVals, bounds, numIterations, front_or_rear)

        return suspensionPoints
    #------------------------- END OPTIMIZE FUNCTIONS ---------------------------

if __name__ == "__main__":
    tireDataPath = 'A1965run18.csv'
    suspensionCSVFilePath = 'suspension_points_2020.csv'
    tirePressureCriteria = ['P', 9.5, 10.5]
    FZmin = -200     #lb
    FZmax = 0
    wheelRate = 585  #lb/in
    optIterations = 1
    front_or_rear = 'REAR'
    geometryObj = geometryOptimizer()
    geometryObj.get_optimal_geometry(tireDataPath, suspensionCSVFilePath, tirePressureCriteria, FZmin, FZmax, wheelRate, optIterations, front_or_rear)

    #--------------------- Set File Parameters ------------------------
    # FILE_PATH = "/Users/linda/Documents/PRE/Suspension-Dynamics-master/Xerxes/Suspension-Simulator-Master"
    # FILE = 'A1965run18.csv'
    # tireClient = tireFit(FILE_PATH+'/'+FILE)
    #------------------- Get Tire Fit Parameters ----------------------
    # PRESSURE_CRITERIA = ['P', 9.5, 10.5]
    # mus, cambers, normals = tireClient.getMaxMu_OptimalCamber_vs_NormalForce(PRESSURE_CRITERIA, 200)
    # normal_fit, optimalCamber_fit = tireClient.fit_poly(normals, cambers, 3, True, [-300,0,3000])
    #------------- Get Optimal Suspension Fit Parameters --------------
    # FRONT_WHEEL_RATE = 390  #lb/in
    # REAR_WHEEL_RATE = 585   #lb/in
    # FZ_MIN = -200           #lb
    # FZ_MAX = 0              #lb lol

    # geometryClient = geometryOptimizer()
    # displacements_front, optimalCambers_front = geometryClient.get_optimal_camber_displacement_curve(FRONT_WHEEL_RATE,
            # FZ_MIN, FZ_MAX, normal_fit, optimalCamber_fit)
    # displacements_rear, optimalCambers_rear = geometryClient.get_optimal_camber_displacement_curve(REAR_WHEEL_RATE,
            # FZ_MIN, FZ_MAX, normal_fit, optimalCamber_fit)
    
    #-------- Get Real Suspension Fit Parameters and Optimized ----------
    # suspensionStateBase = base().read_suspension_csv('suspension_points_2019.csv')
    # suspensionStateOptimized = base().read_suspension_csv('suspension_points_2019_opt1.csv')
    
    # kinematicsObj = kinematics()
    # baseCambers_front = kinematicsObj.get_cambers(displacements_front, 'FRONT', suspensionStateBase)
    # optimizedCambers_front = kinematicsObj.get_cambers(displacements_front, 'FRONT', suspensionStateOptimized)
    # baseCambers_rear = kinematicsObj.get_cambers(displacements_rear, 'REAR', suspensionStateBase)
    # optimizedCambers_rear = kinematicsObj.get_cambers(displacements_rear, 'REAR', suspensionStateOptimized)

    # import matplotlib.pyplot as plt
    # fig = plt.figure(figsize=plt.figaspect(0.3))

    # x = fig.add_subplot(1,2,1)
    # ax.plot(displacements_front, optimizedCambers_front, label='optimized')
    # ax.plot(displacements_front, optimalCambers_front, label='optimal')
    # ax.plot(displacements_front, baseCambers_front, label='base')
    # ax.legend()
    # ax.set_title('Front Suspension: Camber vs. Displacement [Wheel Rate 390 lb/in]')
    # ax.set_xlabel('Displacement', fontsize=10)
    # ax.set_ylabel('Camber', fontsize=10)

    # ax = fig.add_subplot(1,2,2)
    # ax.plot(displacements_rear, optimizedCambers_rear, label='optimized')
    # ax.plot(displacements_rear, optimalCambers_rear, label='optimal')
    # ax.plot(displacements_rear, baseCambers_rear, label='base')
    # ax.legend()
    # ax.set_title('Rear Suspension: Camber vs. Displacement [Wheel Rate 585 lb/in]')
    # ax.set_xlabel('Displacement', fontsize=10)
    # ax.set_ylabel('Camber', fontsize=10)
    
    # plt.show()
    #------------------------- Plot Curves -----------------------------
    # import pandas as pd
    # from plot import plot 
    
    # d = {'CAM': optimalCambers, 'DIS':displacements}
    # data = pd.DataFrame(d)
    # units = {'CAM': 'Degree', 'DIS': 'Inches'}
    # x = {'Column':'DIS', 'Name':'Displacement From Rest'}
    # y = {'Column':'CAM', 'Name':'Optimal Camber'}
    # filterCriteria = {}
    # filterPositive = False

    # # empty argument to plot
    # plotClient = plot('')
    # plotClient.plot_data(x, y, filterCriteria, filterPositive, [data, units])

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
