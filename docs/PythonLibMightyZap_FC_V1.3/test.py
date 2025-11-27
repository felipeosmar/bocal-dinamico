import sys
import serial
import PythonLibMightyZap_FC
import time

MightyZap = PythonLibMightyZap_FC

Actuator_ID = 0

MightyZap.OpenMightyZap('COM21 ',57600)
time.sleep(0.1)
pos =0

MightyZap.GoalPosition(Actuator_ID,3000)
while pos < 2990 :
    pos = MightyZap.PresentPosition(Actuator_ID)
    print(pos)

MightyZap.GoalPosition(Actuator_ID,0)
while pos > 10 :
    pos = MightyZap.PresentPosition(Actuator_ID)
    print(pos) 
    

