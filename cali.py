import json
import csv
from time import sleep
import RPi.GPIO as gpio
import math

#GPIO Settings
DIR = [26,22,6,17,25,23]
STEP = [13,27,5,4,12,24]
CW =1
CCW =0

f = open("c_m_p.txt", 'w')
f.write(str(0)+'\n')
f.write(str(0)+'\n')
f.write(str(0)+'\n')
f.write(str(0)+'\n')
f.write(str(0)+'\n')
f.write(str(0)+'\n')
f.close()

motor_busy = 0

steps = [0,0,0,0,0,0]

gpio.setmode(gpio.BCM)
gpio.setup(DIR, gpio.OUT)
gpio.setup(STEP, gpio.OUT)

def move_step(motor,step):
    duration = 0.01
    n = int(motor)
    gpio.output(DIR[n],CW)
    for i in range(step):
        gpio.output(STEP[n],gpio.HIGH)
        sleep(duration)
        gpio.output(STEP[n],gpio.LOW)
    sleep(3)
    gpio.output(DIR[n],CCW)
    for i in range(step):
        gpio.output(STEP[n],gpio.HIGH)
        sleep(duration)
        gpio.output(STEP[n],gpio.LOW)
    return 0

def move():
    chk = 1
    while chk:
        order = input()
        motor = order.split(' ')[0]
        if motor == "save":
            save()
        elif motor == "end":
            chk = 0
            break
        else:
            step = order.split(' ')[1]
            steps[int(motor)] = int(step)
            move_step(motor,step)
        
def save():
    f = open("steps.txt", 'w')
    f.write(str(steps[0])+'\n')
    f.write(str(steps[1])+'\n')
    f.write(str(steps[2])+'\n')
    f.write(str(steps[3])+'\n')
    f.write(str(steps[4])+'\n')
    f.write(str(steps[5])+'\n')
    f.close()
    return '저장되었습니다.'

move()

gpio.cleanup()
