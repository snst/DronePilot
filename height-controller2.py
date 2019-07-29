#!/usr/bin/env python
import PySimpleGUI as sg
import time, datetime, csv, threading
from math import *
from modules.utils import *
from modules.utils2 import *
from modules.pyMultiwii import MultiWii


TCP_IP = "127.0.0.1" # Localhost (for testing)
TCP_PORT = 3333 # 51001 # This port match the ones using on other scripts

vehicle = MultiWii(TCP_IP, TCP_PORT)


layout = [      
    [sg.Text('allo', size=(8, 2), font=('Helvetica', 20), justification='center', key='text')],
    [sg.Text('Alt:', font=('Helvetica', 20)),
     sg.Text('123', font=('Helvetica', 20), key='alt_current')],
    [sg.Text('Alt', font=('Helvetica', 20)),
     sg.Slider(range=(1, 200), orientation='h', size=(20, 20), default_value=25, key='alt_dest')],     
    [sg.Text('P', font=('Helvetica', 20)),
     sg.Slider(range=(1, 100), orientation='h', size=(20, 20), default_value=25, key='sp')],     
    [sg.Text('I', font=('Helvetica', 20)),
     sg.Slider(range=(1, 100), orientation='h', size=(20, 20), default_value=75, key='si')],      
    [sg.Text('D', font=('Helvetica', 20)),
     sg.Slider(range=(1, 100), orientation='h', size=(20, 20), default_value=10, key='sd')]
]

window = sg.Window('alt controller', default_element_size=(40, 1)).Layout(layout)


current_time = 0
paused = False
start_time = int(round(time.time() * 100))
currentAlt = 1
while (True):
    event, values = window.Read(timeout=10)
    current_time = int(round(time.time() * 100)) - start_time
    window.FindElement('text').Update('{:02d}:{:02d}.{:02d}'.format((current_time // 100) // 60,
                                                                  (current_time // 100) % 60,
                                                                  current_time % 100))

    currentAlt = vehicle.getData(MultiWii.MSP_SONAR_ALTITUDE) / 100.0
    window.FindElement('alt_current').Update('{:f}'.format(currentAlt))

    if event is None or event == 'Exit':
        break
    #print(event, values)
    #print(values['alt'])
window.Close()