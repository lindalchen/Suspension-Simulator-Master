#------------------- DESCRIPTION -------------------# 
# This program serves as a base program for all 
# optimization routines. 
#------------------- USAGE -------------------------#
# instantiate an object and call the appropriate 
# methods 
#---------------------------------------------------#
#------------------- AUTHOR ------------------------#
# @ Xerxes Libsch 5/16/2020
#---------------------------------------------------#

import scipy.optimize as sciOptimize
import csv
import random
import joblib

from base import base
from kinematics import kinematics
from joblib import Parallel, delayed


class optimize(base):
    def __init__(self):
        pass 
    #------------------------- OPTIMIZE FUNCTIONS ---------------------------
    # optimize. Pass two lists. Fit list2 to list1 based on params. optMethod of optObj
    # generates list 2
    def optimize_geometry(self, optimalCambers, displacements, suspensionCSVFile,
        zRange, deltaZ, initialParamGuess, bnds, iterations, front_or_rear):    
        kinematicsObj = kinematics()
        suspensionState = self.read_suspension_csv(suspensionCSVFile)
        actualCambers = kinematicsObj.get_cambers(displacements, front_or_rear, suspensionState)

        for i in range(len(bnds)):
            if ((initialParamGuess[i] > bnds[i][1]) | (initialParamGuess[i] < bnds[i][0])):
                print(i)

        assert(len(optimalCambers) == len(actualCambers)), 'ERROR: Lists must be the same length'

        fun = lambda x: (self.calculate_squared_error(optimalCambers,
            kinematicsObj.get_cambers(displacements, front_or_rear, self.convert_kinematic_state_to_pointDict(x)),
                                                      self.convert_kinematic_state_to_pointDict(x)))
        
        # distribute process using multithreading to speed up
        guesses = [self.induce_perturbations(initialParamGuess, bnds) for attempt in range(0, iterations)] # was originally ParamGuess
        results = []

        for guess in guesses:
            res = sciOptimize.minimize(fun, guess, method='TNC', bounds=bnds, tol=1e-8) #guess was initialparamguess
            squaredError = self.calculate_squared_error(optimalCambers,
            kinematicsObj.get_cambers(displacements, front_or_rear, self.convert_kinematic_state_to_pointDict(res.x)), res.x)
            results.append(res)

        globalOptimum = []
        minSquaredError = float('inf')

        for res in results:
            squaredError = self.calculate_squared_error(optimalCambers,
            kinematicsObj.get_cambers(displacements, front_or_rear,
            self.convert_kinematic_state_to_pointDict(res.x)), res.x)
            print(res.x)
            print('TOTAL SQUARED ERROR: %f \n' % squaredError)
            if squaredError < minSquaredError:
                minSquaredError = squaredError
                globalOptimum = res.x

        return self.convert_kinematic_state_to_pointDict(globalOptimum)
    #------------------------- END OPTIMIZE FUNCTIONS ---------------------------

    #--------------------------- SUPPORT FUNCTIONS ------------------------------
    # calculate squared error between two corresponding data sets
    def calculate_squared_error(self, list1, list2, x):
        assert(len(list1) == len(list2)), 'ERROR: Lists must be the same length'
        squaredError = 0.0
        for num, fit in zip(list1, list2):
            squaredError += (float(fit)-float(num))**2
        print('NEXT ITERATION', squaredError)
        
        if squaredError < 300: 
            print(x)
        return squaredError  
    # introduce random perturbation in intial conditions 

    def induce_perturbations(self, initialGuess, bnds):
        assert(len(initialGuess) == len(bnds)), 'ERROR: Bounds and initial guess must have the same length'
        perturbedGuess = [random.uniform(bound[0], bound[1]) for bound in bnds]
        return tuple(perturbedGuess)

    # convert current state of optimization geometry to pass to kinematics
    def convert_kinematic_state_to_pointDict(self, stateVector):
        # order of variables within optimizing tuple output 
        orderDict = self.get_order_mapping()
        pointDict = {}
        for key in orderDict.keys():
            pointDict[orderDict[key]]= []
        count = 0
        position = 0
        for param in stateVector:
            if position == 14:
                position += 1
            else:
                if count % 3 == 0 and count != 0:
                    position += 1
            # state is in form: (param1 x, param1 y, param1 z ...)
            pointDict[orderDict[position]].append(param)
            # we get to camber offset, which only has one field
            count += 1
        return pointDict

    # return bounds for a given set of variables 
    def get_bounds_list(self, csvPath):
        orderDict = self.get_order_mapping()
        nameMaps = self.get_name_position_map()
        boundsList = []

        with open(csvPath) as csvfile:
            csvfile = csv.reader(csvfile, delimiter=',')
            for row in csvfile:
                if (row[0] in nameMaps.keys()):
                    boundsList.append([])
                    if (row[0] in ['Front camber offset relative to kingpin', 'Rear camber offset relative to kingpin']):
                        for x in [2]:
                            boundsPair = (float(row[x]), float(row[x+1]))
                            position = nameMaps[row[0]]
                            boundsList[position].append(boundsPair)
                    else:
                        for x in [4, 6, 8]:
                            boundsPair = (float(row[x]), float(row[x+1]))
                            position = nameMaps[row[0]]
                            boundsList[position].append(boundsPair)  
        bounds = []
        for setsOfBounds in boundsList:
            for bound in setsOfBounds:
                bounds.append(bound)
        return bounds

    # get initial parameter guess for suspension 
    def get_initial_param_guess(self, suspensionCSVFile):
        orderDict = self.get_order_mapping()
        nameMaps = self.get_name_position_map()
        paramList = []

        with open(suspensionCSVFile) as csvfile:
            csvfile = csv.reader(csvfile, delimiter=',')
            for row in csvfile:
                if (row[0] in nameMaps.keys()):
                    if (row[0] in ['Front camber offset relative to kingpin', 'Rear camber offset relative to kingpin']):
                        for x in [1]:
                            paramList.append(float(row[x]))
                    else:
                        for x in [1,2,3]:
                            paramList.append(float(row[x]))
        return paramList
    #--------------------------- END SUPPORT FUNCTIONS ------------------------------
    
if __name__ == "__main__":
    optimizer = optimize()
    nameMap = optimizer.get_initial_param_guess('suspension_points.csv')
