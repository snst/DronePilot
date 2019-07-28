#!/usr/bin/env python
""" Drone Pilot - Control of MRUAV """
""" mw-height-controller.py: Script that calculates throttle command for a vehicle 
    with MultiWii flight controller and a HC-SR04 sonar in order to keep a specified altitude."""

__author__ = "Aldo Vargas"
__copyright__ = "Copyright 2016 Altax.net"

__license__ = "GPL"
__version__ = "1"
__maintainer__ = "Aldo Vargas"
__email__ = "alduxvm@gmail.com"
__status__ = "Development"

import time, datetime, csv, threading
from math import *
from modules.utils import *
from modules.utils2 import *
from modules.pyMultiwii import MultiWii


TCP_IP = "127.0.0.1" # Localhost (for testing)
TCP_PORT = 5761 # 51001 # This port match the ones using on other scripts


# Main configuration
update_rate = 0.01 # 100 hz loop cycle
vehicle_weight = 0.84 # Kg
u0 = 1000 # Zero throttle command
uh = 1500 # Hover throttle command
kt = vehicle_weight * g / (uh-u0)

# MRUAV initialization
vehicle = MultiWii(TCP_IP, TCP_PORT)

# Initialize RC commands and pitch/roll to be sent to the MultiWii 
rcCMD = [1500,1500,1500,1000]
desiredThrottle = 1000

# PID modules initialization
heightPID = PID2(0.02, 0.05, 0.1)
hPIDvalue = 0.0

# Function to update commands and attitude to be called by a thread
def control():
    global vehicle, rcCMD
    global heightPID
    global desiredPos, currentPos
    global desiredThrottle
    global hPIDvalue
    isEnabled = True
    currentAlt = 100
    desiredAlt = 100

    try:
        while True:

            currentAlt = vehicle.getData(MultiWii.MSP_SONAR_ALTITUDE) / 100.0
            
            errorAlt = desiredAlt - currentAlt

            hPIDvalue = heightPID.update(errorAlt)

            desiredThrottle = ((hPIDvalue + g) * vehicle_weight)
            desiredThrottle = (desiredThrottle / kt) + u0
            print "sonar: current: %f, desired: %f, error: %f, pid: %f, Th: %d" % (currentAlt, desiredAlt, errorAlt, hPIDvalue, desiredThrottle)

            # Limit commands for safety
            if isEnabled:
                rcCMD[0] = 0
                rcCMD[1] = 0
                rcCMD[2] = limit(desiredThrottle,1000,2000)
                rcCMD[3] = 0
                mode = 'Auto'
            else:
                # Prevent integrators/derivators to increase if they are not in use
                #heightPID.resetIntegrator()
                mode = 'Manual'
            #rcCMD = [limit(n,1000,2000) for n in rcCMD]

            # Send commands to vehicle
            vehicle.sendCMD(8,MultiWii.SET_RAW_RC,rcCMD)

            #print "Mode: %s | Z: %0.3f | FilterZ: %0.3f | Throttle: %d " % (mode, currentPos['z'], currentPos['z'], rcCMD[3])

            time.sleep(0.05)

    except Exception,error:
        print "Error in control thread: "+str(error)

if __name__ == "__main__":
        control()
        exit()