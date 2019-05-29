# 아두이노랑 통신을 해서 cnc를 움직이고 로봇팔은 거기에 매달려서 움직인다.
# 여기서 이루어지는 것은 아두이노에 움직이는 Gcode를 날리고 완료되면 로봇팔의 동작을 수행하고 이것을 반복한다.
# 정해진 코드가 있어야하고 랜덤을 넣을 예정이다.
# Gcode의 좌표는 절대좌표로 날라간다.
# 해당 Gcode에서 로봇팔이 벽에 부딫치는 것을 예방해야함을 항상 명심
import json
from time import sleep
import RPi.GPIO as gpio
import math
import serial

# 초기 아두이노 시리얼 셋팅
ser = serial.Serial("/dev/ttyACM0",9600)
sleep(5)
ser.flushInput()
ser.flushOutput()
# 로봇팔 초기 셋팅
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
# step setup 90도당 몇스텝이냐.
motor_steps = []
try:
    f = open("steps.txt", 'r')
    for i in range(6):
        line =f.readline()
        motor_steps.append(int(line))
        if not line: break
    f.close()
except:
    motor_steps = [100,100,100,100,100,100]
motor_busy = 1
cnc_busy = 1

# JSON불러와서 로봇팔 움직이는 함수
def move_robotarm(file_name):
    m = read_json(file_name)
    for motor_s in m:
        motor_busy = move_motor(motor_s)
        while motor_busy:
            sleep(0.1)
        motor_busy = 1
    return 0

def read_json(m):
    # 파일에서 json을 읽어오기
    try:
        filename = m + '.json'
        with open(filename) as json_file:  
            json_data = json.load(json_file)
    except:
        return "noData"
    return json_data

def move_motor(motor):
    c_m_p=[]
    gpio.setmode(gpio.BCM)
    gpio.setup(DIR, gpio.OUT)
    gpio.setup(STEP, gpio.OUT)
    try:
        f = open("c_m_p.txt", 'r')
        for i in range(6):
            line =f.readline()
            c_m_p.append(float(line))
            if not line: break
        f.close()
    except:
        c_m_p = [0,0,0,0,0,0]
    if len(c_m_p) < 6:
        c_m_p = [0,0,0,0,0,0]
    min_speed = 0.001
    max_speed = 0.0002
    acc = 0.00005
    gap = (min_speed-max_speed)/acc
    duration = min_speed
    m=[]
    m.append(int((motor['m0'] - c_m_p[0])*2/math.pi*motor_steps[0]))
    m.append(int((motor['m1'] - c_m_p[1])*2/math.pi*motor_steps[1]))
    m.append(-int((motor['m2'] - c_m_p[2])*2/math.pi*motor_steps[2]))#방향이 반대라서 - 붙임
    m.append(int((motor['m3'] - c_m_p[3])*2/math.pi*motor_steps[3]))
    m.append(int((motor['m4'] - c_m_p[4])*2/math.pi*motor_steps[4]))
    m.append(int((motor['m5'] - c_m_p[5])*2/math.pi*motor_steps[5]))
    #방향 정하고
    for i in range(len(m)):
        if m[i] > 0:
            gpio.output(DIR[i],CW)
        else:
            gpio.output(DIR[i],CCW)
            m[i]=-m[i]
    # max step 찾고
    max_step = m[0]
    
    for a in m:
        if max_step<a:
            max_step = a
    # 다른 것들 step 나누고
    m_div_step = []
    for a in m:
        try:
            m_div_step.append(math.ceil(max_step/a)-1)
        except:
            m_div_step.append(max_step)

    check_m = [0,0,0,0,0,0]
    current_step = 0

    

    # for문 돌고
    for i in range(max_step):
        for i in range(len(m)):
            if check_m[i] == 0 and m[i] != 0:
                gpio.output(STEP[i],gpio.HIGH)
                m[i]-=1
        sleep(duration)
        # 돌면서 나눈 스텝 끝난애들 멈추고
        for i in range(len(m)):
            gpio.output(STEP[i],gpio.LOW)
            if check_m[i] == m_div_step[i]:
                check_m[i]=0
            else:
                check_m[i]+=1
        # 스피드는 맥스까지 올렸다가
        # max랑 min 사이에 change 차이만큼 남았을 때
        # duration 낮춤
        if max_step - current_step < gap:
            duration+=acc
        elif current_step < gap:
            duration-=acc

        current_step += 1

    f = open("c_m_p.txt", 'w')
    f.write(str(motor['m0'])+'\n')
    f.write(str(motor['m1'])+'\n')
    f.write(str(motor['m2'])+'\n')
    f.write(str(motor['m3'])+'\n')
    f.write(str(motor['m4'])+'\n')
    f.write(str(motor['m5'])+'\n')
    f.close()
    gpio.cleanup()
    return 0

# 아두이노에 Gcode 날려주는 함수
def move_cnc(x,y):
    strings = "G "+str(x)+" "+str(y)+"\n"
    ser.write(str.encode(strings))
    while True:
        if ser.readline() == b'done\n':
            break
        sleep(0.1)
    return 0

# 메인 뤂
while True:
    # cnc 움직임
    wait_cnc = 1
    wait_cnc = move_cnc(3000,3000)
    while wait_cnc:
        sleep(0.1)
    sleep(1)
    # 로봇팔 움직임
    wait_robot = 1
    wait_robot = move_robotarm("jola1")
    while wait_robot:
        sleep(0.1)
    sleep(1)
    # cnc 움직임
    wait_cnc = 1
    wait_cnc = move_cnc(0,0)
    while wait_cnc:
        sleep(0.1)
    sleep(1)
    # 로봇팔 움직임
    wait_robot = 1
    wait_robot = move_robotarm("jola2")
    while wait_robot:
        sleep(0.1)
    sleep(1)
