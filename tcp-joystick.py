#!/usr/bin/env python

"""send-joystick.py: Reads a joystick device using pygame and sends the information via UDP."""

__author__ = "Aldo Vargas"
__copyright__ = "Copyright 2016 Altax.net"

__license__ = "GPL"
__version__ = "1"
__maintainer__ = "Aldo Vargas"
__email__ = "alduxvm@gmail.com"
__status__ = "Development"


import struct, time
import pygame
from modules.utils import *
from modules.pyMultiwii import MultiWii
from time import sleep


# Main configuration
TCP_IP = "127.0.0.1" # Localhost (for testing)
TCP_PORT = 5761 # 51001 # This port match the ones using on other scripts

update_rate = 0.1 # 100 hz loop cycle
vehicle = MultiWii(TCP_IP, TCP_PORT)


def init_axix():
    return [-0.2, 0.2]

def update_axis(axis, values, reverse):
    val = joystick.get_axis(axis)
    if reverse:
        val = -val
    values[0] = min(values[0], val)
    values[1] = max(values[1], val)
    return mapping(val,values[0],values[1],1000,2000)

def update_button(axis, values):
    val = joystick.get_button(axis)
    values[0] = min(values[0], val)
    values[1] = max(values[1], val)
    return mapping(val,values[0],values[1],1200,1800)


roll_state = init_axix()
pitch_state = init_axix()
yaw_state = init_axix()
throttle_state = init_axix()
aux1_state = init_axix()
aux2_state = init_axix()
aux3_state = init_axix()
aux4_state = init_axix()
online = False
last_aux4 = 0

try:
    pygame.init()
    pygame.mixer.quit()
    #pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
except Exception,error:
    print "No joystick connected on the computer, "+str(error)

starttime = time.time()
i = 0


while True:
    current = time.time()
    elapsed = current - starttime
    i += 1
    
    # Joystick reading
    pygame.event.pump()
    
    roll = update_axis(0, roll_state, False)
    pitch = update_axis(1, pitch_state, True)
    yaw = update_axis(4, yaw_state, False)
    throttle = update_axis(2, throttle_state, True)
    aux1 = update_axis(3, aux1_state, False)
    aux2 = update_button(0, aux2_state)
    aux3 = update_button(1, aux3_state)
    aux4 = update_button(2, aux4_state)

    # RC commnads to be sent to the MultiWii 
    #print "Roll=" + str(joystick.get_axis(0)) + ", Pitch=" + str(joystick.get_axis(1)) + ", Yaw= " + str(joystick.get_axis(4)) + ", Throttle=" + str(joystick.get_axis(2))

    #if elapsed > 10:

    if aux4 > 1500 and last_aux4 != aux4:
        online = not online
    last_aux4 = aux4

    rcCMD1 = [1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8]
    vehicle.sendCMD(36,MultiWii.SET_RAW_RC,rcCMD1)


    rcCMD = [roll,pitch,throttle,yaw,aux1,aux2,aux3,aux4,0,0,0,0,0,0,0,0,0,0]
    if online:
        vehicle.sendCMD(36,MultiWii.SET_RAW_RC,rcCMD)
        print "online #" + str(i)
    else:
        print "offline #" + str(i)

    print rcCMD

    # Be sure to always send the data as floats
    # The extra zeros on the message are there in order for the other scripts to do not complain about missing information
    #message = [roll, pitch, yaw, throttle, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    #buf = struct.pack('>' + 'd' * len(message), *message)
    #sock.sendto(buf, (UDP_IP, UDP_PORT))
    
    #print message

    # Make this loop work at update_rate
    #while elapsed < update_rate:
    #    elapsed = time.time() - current
    time.sleep(0.005)
