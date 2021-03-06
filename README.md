# Robot-Arm-Python-GUI-Control
## 인트로
라즈베리파이로 GUI컨트롤하는 로봇팔입니다.  
현재 [BCN3D-Moveo](https://github.com/BCN3D/BCN3D-Moveo)의 프로젝트가 적용되어 있습니다.  
언제든지 마음대로 바꿔서 쓰실 수 있습니다.  
flask를 이용해서 웹서버를 구축하고 로컬에서 접속해서 모터를 컨트롤 하는 구조입니다.  

시연 영상  
[![시연영상1](http://img.youtube.com/vi/qU8u063SvTo/0.jpg)](https://youtu.be/qU8u063SvTo)
[![시연영장2](http://img.youtube.com/vi/PwQUhTsfB9M/0.jpg)](https://youtu.be/PwQUhTsfB9M)


## 라즈베리파이 핀맵(GPIO)  

| 모터                  | 스텝                 | 방향          |
| :------------------- | -------------------: |:---------------:|
| 0번                  | 13 | 26 |
| 1번                 | 27                 | 22            |
| 2번                  | 5                  | 6             |
| 3번                   | 4                   | 17              |
| 4번                   | 12                   | 25              |
| 5번                   | 24                   | 23              |

![핀맵 이미지](https://github.com/HyeokjuJang/Robot-Arm-Python-GUI-Control/raw/master/robotarm_bb.jpg)

## 실행해봅시다.

cali.py로 우선 모터 스텝 셋팅을 합니다.  
실행 후 터미널에서 '1 100' 을 입력하면 1번모터를 100스텝 이동시켰다가 3초 후 원상복구합니다.  
이 움직임이 정확히 90도가 되도록 스텝을 바꾸며 수정하고 모든 모터를 90도에 맞게 수정합니다. 그리고 save를 입력하면 steps.txt를 생성합니다  
end를 입력하고 종료합니다.

index.py를 실행하면 flask앱이 실행되어 웹브라우저로 접속할 수 있습니다. 접속하면 컨트롤 할 수 있는 페이지가 나타납니다. 라즈베리파이 상에서 하지 않고 외부 기기에서 동작이 가능합니다.
