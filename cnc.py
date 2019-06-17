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
import random
import sys

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

#랜덤에서 활용할 함수
def find_nearest(xyz_array,x,y):
    distance=[]
    for i in range(len(xyz_array)):
        distance.append((xyz_array[i][0]-x)*(xyz_array[i][0]-x) + (xyz_array[i][1]-y)*(xyz_array[i][1]-y))
    return distance.index(min(distance))

def calc_xy(r2,r3,m0_v,m2_v):
    return [r2*math.sin(m0_v*math.pi/180)+r3*math.sin(m0_v*math.pi/180+m2_v*math.pi/180),r2*math.cos(m0_v*math.pi/180)+r3*math.cos(m0_v*math.pi/180+m2_v*math.pi/180)]

def r(n):
    return random.random()*n

# RANDOM으로 졸라맨 그리는 함수 인풋으로 m1모터의 각도를 받음. m은 모두 라디안
# m['m0'] 이런식으로 넘겨야함
def random_zola(m1):
    motor = [0,0,0,0,0,0]

    motor[1] = m1 * math.pi / 180 # 라디안으로 변환
    m = []

    # 모터 그림 초기화는 모터0 60도 모터2 -60도
    motor[0] = 60
    motor[2] = -60

    # 손쉬운 튜닝을 위한 변수들 랜덤도 여기에 추가
    # 랜덤함수 r(max값)
    brush_h = 20
    h2b = 10*r(3)
    b2la = [5*r(3),4*r(5)]
    la2lh = [3*r(3),4*r(5)]
    b2ra = [5*r(3),4*r(5)]
    ra2rh = [3*r(3),4*r(5)]
    b2b = 12*r(3)
    b2ln = [2*r(3),10*r(3)]
    ln2lf = [2*r(3),10*r(3)]
    b2rn = [2*r(3),10*r(3)]
    rn2rf = [2*r(3),10*r(3)]

    # 현재 위치 계산하고 가장 가까운 모터0,2 찾고 모터4를 직각으로 할당하고 append
    [c_x,c_y] = calc_xy(r2,r3,motor[0],motor[2])
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x,c_y)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})
    head=m[len(m)-1]

    #머리 점찍기
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x,c_y+brush_h)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #점찍고 내려오기
    motor[0]=head['m0']*180/math.pi
    motor[1]=head['m1']*180/math.pi
    motor[2]=head['m2']*180/math.pi
    motor[3]=head['m3']*180/math.pi
    motor[4]=head['m4']*180/math.pi
    motor[5]=head['m5']*180/math.pi
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})


    #몸통으로 이동
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x-h2b,c_y)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})
    body = m[len(m)-1]

    #몸통 점찍기
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x,c_y+brush_h)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #왼팔꿈치
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    motor[1]+=b2la[0]
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x+b2la[1],c_y)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #왼손
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    motor[1]+=la2lh[0]
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x+la2lh[1],c_y)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #붓 떼고
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x,c_y-brush_h)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #몸통 돌아오기
    motor[0]=body['m0']*180/math.pi
    motor[1]=body['m1']*180/math.pi
    motor[2]=body['m2']*180/math.pi
    motor[3]=body['m3']*180/math.pi
    motor[4]=body['m4']*180/math.pi
    motor[5]=body['m5']*180/math.pi
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})


    #몸통 점찍기
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x,c_y+brush_h)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #오른팔꿈치
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    motor[1]-=b2ra[0]
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x+b2ra[1],c_y)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #오른손
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    motor[1]-=ra2rh[0]
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x+ra2rh[1],c_y)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #붓 떼고
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x,c_y-brush_h)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #몸통 돌아오기
    motor[0]=body['m0']*180/math.pi
    motor[1]=body['m1']*180/math.pi
    motor[2]=body['m2']*180/math.pi
    motor[3]=body['m3']*180/math.pi
    motor[4]=body['m4']*180/math.pi
    motor[5]=body['m5']*180/math.pi
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #몸통 점찍기
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x,c_y+brush_h)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #골반으로 이동
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x-b2b,c_y)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})
    belly = m[len(m)-1]

    #왼쪽무릎
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    motor[1]+=b2ln[0]
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x-b2ln[1],c_y)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #왼쪽발
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    motor[1]+=ln2lf[0]
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x-ln2lf[1],c_y)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #붓 떼고
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x,c_y-brush_h)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #붓 대기 전골반으로 이동
    motor[0]=belly['m0']*180/math.pi
    motor[1]=belly['m1']*180/math.pi
    motor[2]=belly['m2']*180/math.pi
    motor[3]=belly['m3']*180/math.pi
    motor[4]=belly['m4']*180/math.pi
    motor[5]=belly['m5']*180/math.pi
    [c_x,c_y] = calc_xy(r2,r3,motor[0],motor[2])
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x,c_y-brush_h)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #붓 대기
    motor[0]=belly['m0']*180/math.pi
    motor[1]=belly['m1']*180/math.pi
    motor[2]=belly['m2']*180/math.pi
    motor[3]=belly['m3']*180/math.pi
    motor[4]=belly['m4']*180/math.pi
    motor[5]=belly['m5']*180/math.pi
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #오른쪽무릎
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    motor[1]-=b2rn[0]
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x-b2rn[1],c_y)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #오른쪽발
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    motor[1]-=rn2rf[0]
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x-rn2rf[1],c_y)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    #붓 떼고
    [c_x,c_y] = calc_xy(r2,r3,m[len(m)-1]["m0"]*180/math.pi,m[len(m)-1]["m2"]*180/math.pi)
    [motor[0], motor[2]] = m0_m2[find_nearest(xyz_array,c_x,c_y-brush_h)]
    motor[4] = -motor[0]-motor[2];
    m.append({'m0':motor[0]*math.pi/180,'m1':motor[1]*math.pi/180,'m2':motor[2]*math.pi/180,'m3':motor[3]*math.pi/180,'m4':motor[4]*math.pi/180,'m5':motor[5]*math.pi/180})

    for motor_s in m:
        motor_busy = move_motor(motor_s)
        while motor_busy:
            sleep(0.1)
        motor_busy = 1
    return 0

def move_motor(motor):
    gpio.setmode(gpio.BCM)
    gpio.setup(DIR, gpio.OUT)
    gpio.setup(STEP, gpio.OUT)

    c_m_p=[]
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
    max_speed = 0.0003
    acc = 0.000003
    gap = (min_speed-max_speed)/acc
    duration = min_speed
    m=[] # m은 라디안 값을 갖음. 2/PI*step 인 이유는 스텝이 90도를 기준으로 표준화하기 때문
    m.append(int((motor['m0'] - c_m_p[0])*2/math.pi*motor_steps[0]))
    m.append(int((motor['m1'] - c_m_p[1])*2/math.pi*motor_steps[1]))
    m.append(-int((motor['m2'] - c_m_p[2])*2/math.pi*motor_steps[2]))#방향이 반대라서 - 붙임
    m.append(int((motor['m3'] - c_m_p[3])*2/math.pi*motor_steps[3]))
    m.append(-int((motor['m4'] - c_m_p[4])*2/math.pi*motor_steps[4]))#방향이 반대라서 - 붙임
    m.append(int((motor['m5'] - c_m_p[5])*2/math.pi*motor_steps[5]))
    # DEBUG:

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
            check_m[i]+=1
            if check_m[i] >= m_div_step[i]:
                check_m[i]=0

        # 스피드는 맥스까지 올렸다가
        # max랑 min 사이에 change 차이만큼 남았을 때
        # duration 낮춤
        if current_step < gap:
            duration-=acc
        elif max_step - current_step < gap:
            duration+=acc

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
    sleep(0.4)
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


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if arg == "reset":
            f = open("c_m_p.txt", 'w')
            f.write(str(0)+'\n')
            f.write(str(0)+'\n')
            f.write(str(0)+'\n')
            f.write(str(0)+'\n')
            f.write(str(0)+'\n')
            f.write(str(0)+'\n')
            f.close()
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
    r1=231.5
    r2=221.1
    r3=223
    r4=70
    # 위아래좌우 움직일 정답 표 생성
    m0_arr = [0 for i in range(350)]
    m2_arr = [0 for i in range(350)]
    for i in range(len(m0_arr)):
        m0_arr[i]=i/len(m0_arr)*90;
        m2_arr[i]=-i/len(m2_arr)*130;

    xyz_array = []
    m0_m2 = []
    for m0_v in m0_arr:
        for m2_v in m2_arr:
            xyz_array.append([r2*math.sin(m0_v*math.pi/180)+r3*math.sin(m0_v*math.pi/180+m2_v*math.pi/180),r2*math.cos(m0_v*math.pi/180)+r3*math.cos(m0_v*math.pi/180+m2_v*math.pi/180)]);
            m0_m2.append([m0_v,m2_v])


    # cnc 움직임

    wait_cnc = 1
    wait_cnc = move_cnc(0,0)
    while wait_cnc:
        sleep(0.1)
    sleep(1)
    # 로봇팔 움직임
    wait_robot = 1
    wait_robot = random_zola(0)
    while wait_robot:
        sleep(0.1)
    sleep(1)
    # cnc 움직임
    wait_cnc = 1
    wait_cnc = move_cnc(300,300)
    while wait_cnc:
        sleep(0.1)
    sleep(1)
    # 로봇팔 움직임
    wait_robot = 1
    wait_robot = random_zola(0)
    while wait_robot:
        sleep(0.1)
    sleep(1)
