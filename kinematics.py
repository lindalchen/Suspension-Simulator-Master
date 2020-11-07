# Takes in the static pickup and outboard suspension points (suspension_points.csv) and calculates:
# - camber curve vs. vertical displacement 
# - roll center height vs. vertical displacement
# - roll axis inclination vs. vertical displacement
# - front camber curve vs. steering angle
#
# Exports solution to multiple csv files. Post-processing performed in MATLAB by running postprocess_kinetmatics.mat
#
# Sample suspension point file: sample_suspension_points.csv
#
# Constraints:
# - Only works for 2D profiles. A-arm pickup points must be at the same Z-position. No support for anti-dive/squat pickup profiles yet.
# - Assumes linear relation between vertical wheel displacement and shock force. (Mapping: dF = k*dz)

import math
import csv
from time import time

from base import base

class kinematics(base):
    def __init__(self):
        # holds geometric points // see base.py
        self.points = {}

    def checkConstraints(self, points):
        if (points['FTFC'][2]!=points['FTRC'][2] or points['FBFC'][2]!=points['FBRC'][2] or points['RTFC'][2]!=points['RTRC'][2] or points['RBFC'][2]!=points['RBRC'][2]):
            raise ValueError('ERROR: A-arm chassis pickup points must have the same Z-value per arm.')

        if (points['FTFC'][1]!=points['FTRC'][1] or points['FBFC'][1]!=points['FBRC'][1] or points['RTFC'][1]!=points['RTRC'][1] or points['RBFC'][1]!=points['RBRC'][1]):
            raise ValueError('ERROR: A-arm chassis pickup points must have the same Y-value per arm.')

        if (points['FTCP'][2] != 0 or points['RTCP'][2] != 0):
            raise ValueError('ERROR: Tire contact patch must be on ground (Z = 0).')

        for key in points:
            if (isinstance(points[key], list)):
                if (key in ['FTFC','FTRC', 'FBFC','FBRC','FUK', 
        '               FLK', 'FTCP', 'RTFC', 'RTRC', 'RBFC', 'RBRC', 'RUK', 'RLK', 'RTCP'] and points[key][1] < 0.0):
                    raise ValueError('ERROR: All suspension points must be on right side. (Y > 0).') 

    def getNewPositionFromDisplacement(self, inboardy, inboardz, outboardy, outboardz, deltaz):
        # get arm length
        r = math.sqrt((outboardy - inboardy)**2 + (outboardz - inboardz)**2)

        # displace outboard point by deltaz
        newz = outboardz + deltaz

        # solve new y position 
        newy = math.sqrt(r**2 - (newz - inboardz)**2) + inboardy

        return [newy, newz]


    def solveGeometryFromLowerArmDisplacement(self, front_or_rear, points, deltaz):
        if (front_or_rear == 'FRONT'):
            # displace the bottom A-arm at the lower kingpin point by delta z and get the new lower kingpin point
            newFLK = self.getNewPositionFromDisplacement(points['FBRC'][1], points['FBRC'][2], points['FLK'][1], points['FLK'][2], deltaz)

            # find the new diagonal length (from new lower kingpin point to upper A-arm chassis point) as well as the upper A-arm and kingpin lengths
            diagonal_length = math.sqrt((points['FTRC'][1]-newFLK[0])**2 + (points['FTRC'][2]-newFLK[1])**2)
            upper_arm_length = math.sqrt((points['FTRC'][1]-points['FUK'][1])**2 + (points['FTRC'][2]-points['FUK'][2])**2)
            kingpin_length = math.sqrt((points['FLK'][1]-points['FUK'][1])**2 + (points['FLK'][2]-points['FUK'][2])**2)

            # solve law of cosines to find new kingpin angle relative to the diagonal vector
            B = math.acos((diagonal_length**2 + kingpin_length**2 - upper_arm_length**2)/(2*diagonal_length*kingpin_length))

            # find normal distance (dq) and parallel distance (ds) of the kingpin axis with respect to the diagonal vector
            dq = math.sin(B)*kingpin_length
            ds = math.cos(B)*kingpin_length

            # transform normal and parallel vectors to y,z coordinate system
            parallel_vector = [(points['FTRC'][1] - newFLK[0])/diagonal_length, (points['FTRC'][2] - newFLK[1])/diagonal_length]
            normal_vector = [parallel_vector[1], -parallel_vector[0]]

            # get new upper kingpin point
            newFUK = [newFLK[0] + ds*parallel_vector[0] + dq*normal_vector[0] , newFLK[1] + ds*parallel_vector[1] + dq*normal_vector[1]]

            # return 2D state: lower chassis point, new lower and upper kingpin points, upper chassis point, tire contact patch
            return [[points['FBRC'][1], points['FBRC'][2]], newFLK, newFUK, [points['FTRC'][1], points['FTRC'][2]], [points['FTCP'][1], points['FTCP'][2]]]

        elif (front_or_rear == 'REAR'):
            # displace the bottom A-arm at the lower kingpin point by delta z and get the new lower kingpin point
            newRLK = self.getNewPositionFromDisplacement(points['RBRC'][1], points['RBRC'][2], points['RLK'][1], points['RLK'][2], deltaz)

            # find the new diagonal length (from new lower kingpin point to upper A-arm chassis point) as well as the upper A-arm and kingpin lengths
            diagonal_length = math.sqrt((points['RTRC'][1]-newRLK[0])**2 + (points['RTRC'][2]-newRLK[1])**2)
            upper_arm_length = math.sqrt((points['RTRC'][1]-points['RUK'][1])**2 + (points['RTRC'][2]-points['RUK'][2])**2)
            kingpin_length = math.sqrt((points['RLK'][1]-points['RUK'][1])**2 + (points['RLK'][2]-points['RUK'][2])**2)

            # solve law of cosines to find new kingpin angle relative to the diagonal vector
            B = math.acos((diagonal_length**2 + kingpin_length**2 - upper_arm_length**2)/(2*diagonal_length*kingpin_length))

            # find normal distance (dq) and parallel distance (ds) of the kingpin axis with respect to the diagonal vector
            dq = math.sin(B)*kingpin_length
            ds = math.cos(B)*kingpin_length

            # transform normal and parallel vectors to y,z coordinate system
            parallel_vector = [(points['RTRC'][1] - newRLK[0])/diagonal_length, (points['RTRC'][2] - newRLK[1])/diagonal_length]
            normal_vector = [parallel_vector[1], -parallel_vector[0]]

            # get new upper kingpin point
            newRUK = [newRLK[0] + ds*parallel_vector[0] + dq*normal_vector[0] , newRLK[1] + ds*parallel_vector[1] + dq*normal_vector[1]]

            # return 2D state: lower chassis point, new lower and upper kingpin points, upper chassis point, tire contact patch
            return [[points['RBRC'][1], points['RBRC'][2]], newRLK, newRUK, [points['RTRC'][1], points['RTRC'][2]], [points['RTCP'][1], points['RTCP'][2]]]

        else:
            raise ValueError ('ERROR: solveGeometryFromLowerArmDisplacement requires FRONT or REAR as first argument.')

    def getCamberOffsetFromState(self, state):
        LK = state[1]
        UK = state[2]
        dy = UK[0] - LK[0]
        dz = UK[1] - LK[1]
        return math.degrees(math.atan(dy/dz))

    def getInstantCenterFromState(self, state):
        topdy = state[2][0] - state[3][0] 
        topdz = state[2][1] - state[3][1]
        topslope = topdz/topdy
        topintercept = state[2][1] - topslope*state[2][0]

        botdy = state[1][0] - state[0][0] 
        botdz = state[1][1] - state[0][1]
        botslope = botdz/botdy
        botintercept = state[1][1] - botslope*state[1][0]

        yIC = (botintercept - topintercept)/(topslope - botslope)
        zIC = topslope*yIC + topintercept
        return [yIC, zIC]

    def getRollCenterHeightFromState(self, state):
        TCPy = state[4][0]
        # TCPz = 0 by constraint
        IC = self.getInstantCenterFromState(state)
        ICz = IC[1]
        ICy = IC[0]
        return (ICz * TCPy/(TCPy-ICy))

    def getCamberOffset(self, front_or_rear, points):
        if (front_or_rear == 'FRONT'):
            camberOffset = points['FCO'][0]
        elif (front_or_rear == 'REAR'):
            camberOffset = points['RCO'][0]
        else:
            raise ValueError('ERROR: needs FRONT or REAR as first argument and pointDict as second.')

        return camberOffset
    def getCurves(self, points, front_or_rear, deltaz, zrange):
        nPoints = int(zrange/deltaz)
        start = -nPoints*deltaz
        camberOffset = self.getCamberOffset(front_or_rear, points)

        z = []
        camber = []
        RCheight = []

        for i in range(0, 2*nPoints+1):
            z.append(start + i*deltaz)
            state = self.solveGeometryFromLowerArmDisplacement(front_or_rear, points, start+i*deltaz)
            camber.append(self.getCamberOffsetFromState(state) + camberOffset)
            RCheight.append(self.getRollCenterHeightFromState(state))

        with open(front_or_rear + '_curves.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['dZ (in.)', 'Camber (deg)', 'Roll Center Height (in.)'])
            for i in range (0, len(z)):
                writer.writerow([z[i], camber[i], RCheight[i]])
        return [z, camber, RCheight]

    # get cambers with optional point dict updated 
    def get_cambers(self, displacementList, front_or_rear, points):
        camberOffset = self.getCamberOffset(front_or_rear, points)
        camberList = []
        for displacement in displacementList:
            state = self.solveGeometryFromLowerArmDisplacement(front_or_rear, points, displacement)
            camberList.append(self.getCamberOffsetFromState(state) + camberOffset)
        return camberList

    def main(self, filename, zrange, deltaz, points = {}):
        if not points:
            self.points = self.read_suspension_csv(filename)
        else: 
            self.points = points

        t0 = time()
        self.checkConstraints(self.points)
        front = self.getCurves(self.points, 'FRONT', deltaz, zrange)
        rear = self.getCurves(self.points, 'REAR', deltaz, zrange)
        t1 = time()
        print('RUNTIME: %f' %(t1-t0))
        return front, rear

if __name__ == "__main__":
    kinematicsClient = kinematics()
    kinematicsClient.main('suspension_points.csv', 3, .05)

