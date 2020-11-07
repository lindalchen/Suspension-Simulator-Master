#------------------- DESCRIPTION -------------------# 
# This program plots 3d suspension geometry. 
#------------------- USAGE -------------------------#
# Run this program with the appropriate suspension 
# points file 
#---------------------------------------------------#
#------------------- AUTHOR ------------------------#
# @ Xerxes Libsch 5/16/2020
#---------------------------------------------------#

from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import math

from base import base

def get_caster_angle(points, front_or_rear):
    if front_or_rear == 'FRONT': 
        opp = math.fabs(points['FUK'][2] - points['FLK'][2])
        adj = math.fabs(points['FUK'][0] - points['FLK'][0])
    elif front_or_rear == 'REAR': 
        opp = math.fabs(points['RUK'][2] - points['RLK'][2])
        adj = math.fabs(points['RUK'][0] - points['RLK'][0])
    else:
        return 'INVALID'
    return (90.0-to_degrees(math.atan(float(opp)/float(adj))))

def get_kingpin_angle(points, front_or_rear):
    if front_or_rear == 'FRONT': 
        opp = math.fabs(points['FUK'][2] - points['FLK'][2])
        adj = math.fabs(points['FUK'][1] - points['FLK'][1])
    elif front_or_rear == 'REAR': 
        opp = math.fabs(points['RUK'][2] - points['RLK'][2])
        adj = math.fabs(points['RUK'][1] - points['RLK'][1])
    else:
        return 'INVALID'
    return (90.0-to_degrees(math.atan(float(opp)/float(adj))))

def to_degrees(x):
    return x*(360.0/(2*math.pi))

def plot_3d(points, newPoints):
    # --------PLOT ORIGINAL A-ARMS FRONT--------
    line1X = [points['FTFC'][0], points['FUK'][0], points['FTRC'][0]]
    line1Y = [points['FTFC'][1], points['FUK'][1], points['FTRC'][1]]
    line1Z = [points['FTFC'][2], points['FUK'][2], points['FTRC'][2]]

    line2X = [points['FBFC'][0], points['FLK'][0], points['FBRC'][0]]
    line2Y = [points['FBFC'][1], points['FLK'][1], points['FBRC'][1]]
    line2Z = [points['FBFC'][2], points['FLK'][2], points['FBRC'][2]]

    line3X = [points['FLK'][0], points['FUK'][0]]
    line3Y = [points['FLK'][1], points['FUK'][1]]
    line3Z = [points['FLK'][2], points['FUK'][2]]

    # --------PLOT NEW A-ARMS FRONT--------
    line1X_n = [newPoints['FTFC'][0], newPoints['FUK'][0], newPoints['FTRC'][0]]
    line1Y_n = [newPoints['FTFC'][1], newPoints['FUK'][1], points['FTRC'][1]]
    line1Z_n = [newPoints['FTFC'][2], newPoints['FUK'][2], points['FTRC'][2]]

    line2X_n = [newPoints['FBFC'][0], newPoints['FLK'][0], newPoints['FBRC'][0]]
    line2Y_n = [newPoints['FBFC'][1], newPoints['FLK'][1], newPoints['FBRC'][1]]
    line2Z_n = [newPoints['FBFC'][2], newPoints['FLK'][2], newPoints['FBRC'][2]]

    line3X_n = [newPoints['FLK'][0], newPoints['FUK'][0]]
    line3Y_n = [newPoints['FLK'][1], newPoints['FUK'][1]]
    line3Z_n = [newPoints['FLK'][2], newPoints['FUK'][2]]

    # --------PLOT ORIGINAL A-ARMS REAR--------
    line4X = [points['RTFC'][0], points['RUK'][0], points['RTRC'][0]]
    line4Y = [points['RTFC'][1], points['RUK'][1], points['RTRC'][1]]
    line4Z = [points['RTFC'][2], points['RUK'][2], points['RTRC'][2]]

    line5X = [points['RBFC'][0], points['RLK'][0], points['RBRC'][0]]
    line5Y = [points['RBFC'][1], points['RLK'][1], points['RBRC'][1]]
    line5Z = [points['RBFC'][2], points['RLK'][2], points['RBRC'][2]]

    line6X = [points['RLK'][0], points['RUK'][0]]
    line6Y = [points['RLK'][1], points['RUK'][1]]
    line6Z = [points['RLK'][2], points['RUK'][2]]

    # --------PLOT NEW A-ARMS REAR--------
    line4X_n = [newPoints['RTFC'][0], newPoints['RUK'][0], newPoints['RTRC'][0]]
    line4Y_n = [newPoints['RTFC'][1], newPoints['RUK'][1], points['RTRC'][1]]
    line4Z_n = [newPoints['RTFC'][2], newPoints['RUK'][2], points['RTRC'][2]]

    line5X_n = [newPoints['RBFC'][0], newPoints['RLK'][0], newPoints['RBRC'][0]]
    line5Y_n = [newPoints['RBFC'][1], newPoints['RLK'][1], newPoints['RBRC'][1]]
    line5Z_n = [newPoints['RBFC'][2], newPoints['RLK'][2], newPoints['RBRC'][2]]

    line6X_n = [newPoints['RLK'][0], newPoints['RUK'][0]]
    line6Y_n = [newPoints['RLK'][1], newPoints['RUK'][1]]
    line6Z_n = [newPoints['RLK'][2], newPoints['RUK'][2]]

    fig = plt.figure(figsize=plt.figaspect(0.4))

    # PLOT FRONT 
    ax = fig.add_subplot(1,2,1, projection='3d')
    plt.title('Front Suspension: 2018[Blue], Optimized[Red]')

    ax.plot3D(line1X, line1Y, line1Z, color='blue')
    ax.plot3D(line2X, line2Y, line2Z, color='blue')
    ax.plot3D(line3X, line3Y, line3Z, color='blue')

    ax.plot(line1X, line1Y, zdir='z', color='blue', linestyle='--')
    ax.plot(line2X, line2Y, zdir='z', color='blue', linestyle='--')

    ax.plot3D(line1X_n, line1Y_n, line1Z_n, color='red')
    ax.plot3D(line2X_n, line2Y_n, line2Z_n, color='red')
    ax.plot3D(line3X_n, line3Y_n, line3Z_n, color='red')

    ax.plot(line1X_n, line1Y_n, zdir='z', color='red', linestyle='--')
    ax.plot(line2X_n, line2Y_n  , zdir='z', color='red', linestyle='--')

    # PLOT REAR 
    ax = fig.add_subplot(1,2,2, projection='3d')
    plt.title('Rear Suspension: 2018[Blue], Optimized[Red]')
    ax.plot3D(line4X, line4Y, line4Z, color='blue')
    ax.plot3D(line5X, line5Y, line5Z, color='blue')
    ax.plot3D(line6X, line6Y, line6Z, color='blue')

    ax.plot(line4X, line4Y, zdir='z', color='blue', linestyle='--')
    ax.plot(line5X, line5Y, zdir='z', color='blue', linestyle='--')

    ax.plot3D(line4X_n, line4Y_n, line4Z_n, color='red')
    ax.plot3D(line5X_n, line5Y_n, line5Z_n, color='red')
    ax.plot3D(line6X_n, line6Y_n, line6Z_n, color='red')

    ax.plot(line4X_n, line4Y_n, zdir='z', color='red', linestyle='--')
    ax.plot(line5X_n, line5Y_n, zdir='z', color='red', linestyle='--')

    plt.show()

if __name__ == "__main__":
    points = base().read_suspension_csv('suspension_points.csv')
    new_points = base().read_suspension_csv('suspension_points_2019_opt1.csv')

    print('-------IMPORTANT PARAMETERS--------')
    print('Front Caster Angle:  %f' % get_caster_angle(new_points, 'FRONT'))
    print('Rear Caster Angle:   %f' % get_caster_angle(new_points, 'REAR'))
    print('Front KPI Angle:     %f' % get_kingpin_angle(new_points, 'FRONT'))
    print('Rear KPI Angle:      %f' % get_kingpin_angle(new_points, 'REAR'))
    print('-----------------------------------')

    plot_3d(points, new_points)
