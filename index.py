from flask import Flask,render_template,request
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

#Flask Settings
app = Flask(__name__)

motor_busy = 0

@app.route("/")
def hello():
    return render_template('index.html')
    
@app.route("/move",methods=['POST'])
def move():
    m=json.loads(request.data.decode('utf-8'))
    for motor_s in m:
        motor_busy = move_motor(motor_s)
        while motor_busy:
            time.sleep(0.1)
        motor_busy = 1

    return "done!"

@app.route("/load",methods=['POST'])
def load():
    # 파일에서 json을 읽어오기
    try:
        m=request.data.decode('utf-8')
        filename = m + '.json'
        with open(filename) as json_file:  
            m = json.load(json_file)
        m = json.dumps(m)
    except:
        return "noData"
    return m

@app.route("/save",methods=['POST'])
def save():
    m=json.loads(request.data.decode('utf-8'))
    try:
        filename = m['name']+'.json'
    except:
        return '이름이 없어요.'
    del m['name']
    csvData = m['motor']

    with open(filename, 'w') as outfile:
        json.dump(csvData, outfile)

    outfile.close()
    return filename + '으로 저장되었습니다.'

def move_motor(motor):
    gpio.setmode(gpio.BCM)
    gpio.setup(DIR, gpio.OUT)
    gpio.setup(STEP, gpio.OUT)
    c_m_p=[]
    try:
        f = open("c_m_p.txt", 'r')
        for i in range(6):
            c_m_p.append(int(f.readline()))
            if not line: break
        f.close()
    except:
        c_m_p = [0,0,0,0,0,0]
    if len(c_m_p) < 6:
        c_m_p = [0,0,0,0,0,0]
    min_speed = 0.05
    max_speed = 0.001
    acc = 0.001
    gap = (min_speed-max_speed)/acc
    duration = min_speed
    m=[]
    m.append(int(motor['m0'] - c_m_p[0])*10)
    m.append(int(motor['m1'] - c_m_p[1])*10)
    m.append(int(motor['m2'] - c_m_p[2])*10)
    m.append(int(motor['m3'] - c_m_p[3])*10)
    m.append(int(motor['m4'] - c_m_p[4])*10)
    m.append(int(motor['m5'] - c_m_p[5])*10)
    # max step 찾고
    max_step = m[0]
    for a in m:
        if max_step<a:
            max_step = a
    # 다른 것들 step 나누고
    m_div_step = []
    for a in m:
        try:
            m_div_step.append(math.ceil(max_step/a))
        except:
            m_div_step.append(max_step)

    check_m = [0,0,0,0,0,0]
    current_step = 0

    for i in range(len(m)):
        if m[i] > 0:
            gpio.output(DIR[i],CW)
        else:
            gpio.output(DIR[i],CCW)


    # for문 돌고
    for i in range(max_step):
        for i in range(len(m)):
            if check_m[i] == 0 and m[i] != 0:
                gpio.output(STEP[i],gpio.HIGH)
                m[i]-=1
            else:
                gpio.output(STEP[i],gpio.LOW)
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



if __name__ == '__main__':
   app.run(host='0.0.0.0',port=80,debug = True)