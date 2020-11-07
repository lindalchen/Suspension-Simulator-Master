# Constraints:
# - assumes moment of inertia about center of gravity axis is idealized as a point mass MOI
# - assumes chassis torsional stiffness is infinite (front roll = rear roll)
# - step input is given as a slip angle of 8 deg for both front tires. This can be improved or changed.

import csv
import math

from tireFit import tireFit
from base import base
from kinematics import kinematics

class transient_response(base):
    def __init__(self):
        pass

    def getFittingFunction(self, file, pressureCriteria):
        tireClient = tireFit(file)
        return tireClient.get_fit_object(pressureCriteria) 

    def getLateralForce(self, fitFunc, slipangle, camber, normalforce):
        tireClient = tireFit('')
        return tireClient.get_lateral_force(fitFunc, slipangle, camber, normalforce)
    def getWheelRates(self, constants, front_or_rear):
        if (front_or_rear == 'FRONT'):
            tirerate = constants['FTSR']
            wheelrate = constants['FSSR']*constants['FMR']**2
            return ((1.0/tirerate + 1.0/wheelrate)**(-1))
        elif (front_or_rear == 'REAR'):
            tirerate = constants['RTSR']
            wheelrate = constants['RSSR']*constants['RMR']**2
            return ((1.0/tirerate + 1.0/wheelrate)**(-1))

    def getRollStiffness(self, constants, front_or_rear, track):
        # roll stiffness is torque/deg of roll. Assume +- 1 inch displacement on each wheel.
        # F = 1in*wheelrate on each wheel. Torque = F*track
        # angle = arctan(2in/track)
        wheelrate = self.getWheelRates(constants, front_or_rear)
        angle = math.degrees(math.atan(2.0/track))
        return (12*wheelrate/angle)

    def interpolate(self, xvals, yvals, x):
        for i in range(0, len(xvals)-1):
            if (x >= xvals[i] and x <= xvals[i+1]):
                x0 = xvals[i]
                x1 = xvals[i+1]
                y0 = yvals[i]
                y1 = yvals[i+1]
                return ((x - x0)/(x1 - x0) * (y1 - y0) + y0)
        # throw error if point isn't within the data set
        raise ValueError("ERROR: Trying to interpolate a point outside the data range.")

    def getCamberFromNormalForce(self, curves, normal_force, nominal_normal_force):
        dF = nominal_normal_force - normal_force
        return self.interpolate(curves[0], curves[1], dF)

    def getRCHfromNormalForce(self, curves, normal_force, nominal_normal_force):
        dF = nominal_normal_force - normal_force
        return self.interpolate(curves[0], curves[2], dF)

    def calculateSettlingTime(self, dt, dyawdtlist):
        maxyawgrad = max(dyawdtlist)
        for i in range(0, len(dyawdtlist)):
            if (dyawdtlist[i]/maxyawgrad < 0.01): # if yaw gradient is less than 1% of max yaw gradient
                converged = True
                for j in range(i, len(dyawdtlist)): # check that remaining steps do not exceed 1%
                    if (abs(dyawdtlist[j])/abs(maxyawgrad) > 0.01):
                        converged = False
                if (converged):
                    return(dt*i/100.0)

    def calculateOvershoot(self, dyawdtlist):
        maxyawgrad = max(dyawdtlist)
        minyawgrad = min(dyawdtlist)
        if (minyawgrad > 0.00):
            return (0.00)
        else:
            return (-minyawgrad/maxyawgrad*100.0)

    def calculate_response_time(self, tireFile, suspensionFile):
        dt = 0.1 # time step
        const_slip_angle = 8 # step input for front 
        con_tol_yawgrad = 0.1 # convergence tolerance for yaw gradient

        pressureCriteria = ['P', 9.5, 10.5]
        fitFunc = self.getFittingFunction(tireFile, pressureCriteria)
        constants = self.read_transient_csv(suspensionFile)

        print('')
        print('')
        print('Reading suspension points (suspension_points.csv) and tire fitting function (TireFit/lateral_tire_fitting_function.csv).')

        # right and up are positive from the driver's view

        # ------------- Constants ----------------
        front_track = constants['FTCP'][1] * 2
        rear_track = constants['RTCP'][1] * 2

        wheelbase = constants['RTCP'][0] - constants['FTCP'][0]
        h_cog = constants['COG']
        longitudinal_MOI = 0.5*(constants['FSM'] + constants['RSM'])*h_cog*h_cog

        FR_ss_normal_force = constants['FUM'] + constants['FSM']
        FL_ss_normal_force = constants['FUM'] + constants['FSM']
        RR_ss_normal_force = constants['RUM'] + constants['RSM']
        RL_ss_normal_force = constants['RUM'] + constants['RSM']

        total_mass = 2*(RR_ss_normal_force + FR_ss_normal_force)
        rear_weight_bias = RR_ss_normal_force/(RR_ss_normal_force + FR_ss_normal_force)

        # --------------------------------------


        # ------------ Get curves --------------
        # get camber and RCH curves
        kinematicsObj = kinematics()
        frontcurves, rearcurves = kinematicsObj.main(suspensionFile, 3, .05)
        print(min(rearcurves[0]), max(rearcurves[0]))
        print(min(frontcurves[0]), max(frontcurves[0]))
        frontwheelrate = self.getWheelRates(constants, 'FRONT')
        rearwheelrate = self.getWheelRates(constants, 'REAR')
        print(frontwheelrate)
        print(rearwheelrate)

        # transform curves as a function of delta z to delta normal force
        dF = [x * frontwheelrate for x in frontcurves[0]] #scale dZ to dF
        frontcurves[0] = dF

        dF = [x * rearwheelrate for x in rearcurves[0]]
        rearcurves[0] = dF
        print(min(rearcurves[0]), max(rearcurves[0]))
        print(min(frontcurves[0]), max(frontcurves[0]))

        #--------------------------------------


        # ------- Initial conditions -----------
        yaw = 0
        dyaw_dt = 0
        roll = 0
        droll_dt = 0
        d2roll_dt2 = 0

        FR_lateral_force = 0
        FL_lateral_force = 0
        RR_lateral_force = 0
        RL_lateral_force = 0

        FR_normal_force = FR_ss_normal_force
        FL_normal_force = FL_ss_normal_force
        RR_normal_force = RR_ss_normal_force
        RL_normal_force = RL_ss_normal_force
        print(FR_normal_force, FL_normal_force, RR_normal_force, RL_normal_force)
        # --------------------------------------


        # ------- Calculate coefficients -------

        front_roll_stiffness = self.getRollStiffness(constants, 'FRONT', front_track) + 12.0*constants['FARS'] 
        rear_roll_stiffness =  self.getRollStiffness(constants, 'REAR', front_track) + 12.0*constants['RARS'] 


        # find critical damping coefficients. gamma_crit = sqrt(k*m). k = roll stiffness . m = longitudinal moment of inertia
        front_crit_damping_coeff = math.sqrt(front_roll_stiffness*longitudinal_MOI)
        rear_crit_damping_coeff = math.sqrt(rear_roll_stiffness*longitudinal_MOI)


        # set damping coefficients = damping_ratio*crit_damping_coeff
        front_gamma = constants['FDR']*front_crit_damping_coeff
        rear_gamma = constants['RDR']*rear_crit_damping_coeff

        print(front_roll_stiffness, rear_roll_stiffness, front_crit_damping_coeff, rear_crit_damping_coeff, front_gamma, rear_gamma)
        # --------------------------------------

        # Open output file for writing
        results_yaw      = []
        results_dyawdt   = []
        results_roll     = []
        csvfile = open('output.csv', 'w')
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['t', 'YawGradient', 'Roll', 'FL normal force', 'FR normal force', 'RL normal force', 'RR normal force'])

        print('Starting simulation...')

        for i in range(0, 1000):
            # get new roll center heights and cambers from the normal forces
            front_RCH = .5*self.getRCHfromNormalForce(frontcurves, FR_normal_force, FR_ss_normal_force) + .5*self.getRCHfromNormalForce(frontcurves, FL_normal_force, FL_ss_normal_force)
            rear_RCH = .5*self.getRCHfromNormalForce(rearcurves, RR_normal_force, RR_ss_normal_force) + .5*self.getRCHfromNormalForce(rearcurves, RL_normal_force, RL_ss_normal_force)
            frontleft_camber = self.getCamberFromNormalForce(frontcurves, FL_normal_force, FL_ss_normal_force) 
            frontright_camber = self.getCamberFromNormalForce(frontcurves, FR_normal_force, FR_ss_normal_force) 
            rearleft_camber = self.getCamberFromNormalForce(rearcurves, RL_normal_force, RL_ss_normal_force)
            rearright_camber = self.getCamberFromNormalForce(rearcurves, RR_normal_force, RR_ss_normal_force) 

            # deltaF = roll (deg)  * roll_stiffness(ft-lbs/deg) / track (in) * (12in/ft)
            deltaF = roll*front_roll_stiffness*(h_cog - front_RCH)/h_cog/front_track
            print(deltaF)
            # deltaF is split between the two wheels
            FR_normal_force = FR_ss_normal_force + (0.5*deltaF)
            FL_normal_force = FL_ss_normal_force - (0.5*deltaF)

            # Repeat for rear
            deltaF = roll*rear_roll_stiffness*(h_cog - rear_RCH)/h_cog/rear_track
            RR_normal_force = RR_ss_normal_force + (0.5*deltaF)
            RL_normal_force = RR_ss_normal_force - (0.5*deltaF)

           

            #check if normal force goes negative. If it does, set it to 0
            if (FR_normal_force < 0):
                FR_normal_force = 0
            if (FL_normal_force < 0):
                FL_normal_force = 0
            if (RR_normal_force < 0):
                RR_normal_force = 0
            if (RL_normal_force < 0):
                RL_normal_force = 0 


            # calculate lateral forces using tire fit function for a given slip angle, camber, and normal force
            FR_lateral_force = self.getLateralForce(fitFunc, const_slip_angle, frontright_camber, FR_normal_force)
            FL_lateral_force = self.getLateralForce(fitFunc, const_slip_angle, -frontleft_camber, FL_normal_force)
            RR_lateral_force = self.getLateralForce(fitFunc, yaw - constants['RT'], rearright_camber, RR_normal_force)
            RL_lateral_force = self.getLateralForce(fitFunc, yaw + constants['RT'], -rearleft_camber, RL_normal_force)


            print(FR_lateral_force, 'fr', FR_normal_force)
            print(FL_lateral_force, 'fl', FL_normal_force)
            print(RR_lateral_force, 'rr', RR_normal_force)
            print(RL_lateral_force, 'rl', RL_normal_force)

            # calculate total front and rear lateral forces
            front_force = FR_lateral_force - FL_lateral_force
            rear_force = RR_lateral_force - RL_lateral_force

            # calculate roll torque as a function of the lateral forces and their moment arms with damping in the yz plane
            front_roll_torque = front_force*(h_cog - front_RCH) - front_gamma*droll_dt
            rear_roll_torque = rear_force*(h_cog - rear_RCH) - rear_gamma*droll_dt

            # 2nd derivative of roll is the roll torque divided by moment of inertia
            d2roll_dt2 = (front_roll_torque + rear_roll_torque)/longitudinal_MOI

            # yaw torque is the difference in torques between the front lateral force and rear lateral force on the yaw center (assumed to be center of gravity) in xy plane
            yawtorque = front_force*(1 - rear_weight_bias)*wheelbase - rear_force*rear_weight_bias*wheelbase
            
            # derivative of yaw is the yaw torque divided by the polar moment of inertia. (Not 2nd derivative because we consider yaw to be in the car's reference frame)
            dyaw_dt = 57.296*yawtorque/constants['PMOI'] #57.296 rad/deg

            # Step in time
            yaw += dt*dyaw_dt
            roll += dt*droll_dt
            droll_dt += dt*d2roll_dt2

            results_yaw.append(yaw)
            results_dyawdt.append(-dyaw_dt)
            results_roll.append(roll)

            #write solution
            if (i%10 == 0):
                writer.writerow([i/100.*dt, -dyaw_dt, roll, FL_normal_force, FR_normal_force, RL_normal_force, RR_normal_force])

        err = abs(max(results_dyawdt[-100:], key = abs)) # max absolute value of yaw gradient in last 100 iterations
        if (err < con_tol_yawgrad):
            print('Solution converged to yaw gradient tolerance: ' + str(err))
        else:
            print('Solution did not converge to specified yaw gradient tolerance. Results may be inaccurate. Yaw gradient deviation in last 100 steps: '+ str(err))

        print('')
        print('Results:')
        print('Transient settling time                  :       %.3f' % self.calculateSettlingTime(dt, results_dyawdt) + ' s') #find response time to reach less than 1% of max yaw gradient
        print('Negative yaw-gradient overshoot (%% of max gradient) :       %.1f' % self.calculateOvershoot(results_dyawdt) + ' %')
        print('Steady state yaw                 :       %.1f' % (sum(results_yaw[-100:])/100.0) + ' deg') #average yaw in last 100 iterations
        print('Steady state roll                    :       %.1f' % (sum(results_roll[-100:])/100.0) + ' deg') #average roll in last 100 iterations


if __name__ == "__main__":
    obj = transient_response()
    tireFile = 'A1965run18.csv'
    suspensionFile = 'suspension_points.csv'
    obj.calculate_response_time(tireFile, suspensionFile)
