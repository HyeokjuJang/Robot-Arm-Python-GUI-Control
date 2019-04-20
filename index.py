from flask import Flask,render_template,request
import json
import csv

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')
    
@app.route("/move",methods=['POST'])
def test():
    m=json.loads(request.data)


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
    m=json.loads(request.data)
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

if __name__ == '__main__':
   app.run(debug = True)