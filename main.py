import sys
from threading import Thread
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import numpy as np
import cv2
import mediapipe as mp
import joblib
from collections import Counter
import math
from files.unicode import join_jamos
import sklearn
from tcpMultiThreadServerClass import TCPMultiThreadServer
import socket
from dataheader import *

main_form = uic.loadUiType("./serverChat.ui")[0]


class MainWindow(QMainWindow, main_form):  #큐티메인화면
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.server = TCPMultiThreadServer(port = 2500, listener = 100) # TCPMultiThreadServer 서버 객체 생성

        print("waiting for connection...")
        self.clientSock, addr = self.server.accept()

        self.timer = QTimer(self)
        self.textSend.clicked.connect(self.appendText)
        self.videoBtn.clicked.connect(self.startVideo)
        self.timer.timeout.connect(self.start)


    def appendText(self):
        msg = self.lineEdit.text()
        self.textBrowser.append("user 1 : "+ msg)

        data = ResText(msg)
        self.server.send(self.clientSock, data)

        self.lineEdit.clear()
    
    def startVideo(self):
        self.start()
    
    def signAappend(self, data):        # 수어 영상 ui에 추가시켜주는 부분 + c++로 send하는 부분 추가하기
        self.textBrowser.append("user 1 : "+ data)
        text = ResText(data)
        self.server.send(self.clientSock, text)

    def messageAppend(self, msg):       # c++에서 받은거 ui에 append시켜주는 함수
        text = msg.textMessage
        self.textBrowser.append("user 2 : "+ text)

    def start(self):
        kn = joblib.load('files/ML-model.pkl')
        print("start...")
        cv2.namedWindow('window')
        cap = cv2.VideoCapture(0)
        w = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1)
        feature_list = []

        my_char = ['ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', 'ㅏ', 'ㅑ', 'ㅓ', 'ㅕ', 'ㅗ',
                'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ', 'ㅐ', 'ㅒ', 'ㅔ', 'ㅖ', 'ㅢ', 'ㅚ', 'ㅟ', 'a', 'b', 'c']
        dot_list = [4, 8, 12, 14, 16, 18, 20]
        ja = ['ㄱ','ㄴ','ㄷ','ㄹ','ㅁ','ㅂ','ㅅ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
        mo = ['ㅏ','ㅑ','ㅓ','ㅕ','ㅗ','ㅛ','ㅜ','ㅠ','ㅡ','ㅣ','ㅐ','ㅒ','ㅔ','ㅖ','ㅢ','ㅚ','ㅟ']
        mo1 = ['ㅗ', 'ㅜ']
        mo2 = ['ㅏ', 'ㅐ']
        mo3 = ['ㅓ', 'ㅔ']
        mo4 = ['ㅘ', 'ㅙ', 'ㅝ', 'ㅞ']
        ssang = ['ㄱ','ㄷ','ㅂ','ㅅ','ㅈ']
        jong = [['ㄱ', 'ㅅ', 'ㄳ'], ['ㄴ', 'ㅈ', 'ㄵ'], ['ㄴ', 'ㅎ', 'ㄶ'], ['ㄹ', 'ㄱ', 'ㄺ'], ['ㄹ', 'ㅁ', 'ㄻ'],
                ['ㄹ', 'ㅂ', 'ㄼ'], ['ㄹ', 'ㅅ', 'ㄽ'], ['ㄹ', 'ㅌ', 'ㄾ'], ['ㄹ', 'ㅍ', 'ㄿ'], ['ㄹ', 'ㅎ', 'ㅀ'],
                ['ㅂ', 'ㅅ', 'ㅄ']]
        checker1 = 0
        checker2 = 0
        temp_ch = ''
        my_word = ''
        dump_list = []
        text_list = []
        while (1):
            success, image = cap.read()
            if not success:
                continue
            if len(dump_list) > 30:
                ch = Counter(dump_list).most_common()[0][0]
                if ch != temp_ch:
                    if ch in ja:  # 자음입력
                        for i in range(0, 11):
                            if ch == jong[i][1] and temp_ch == jong[i][0]:
                                my_word = my_word[:-1]
                                my_word += jong[i][2]
                                checker1 = 1
                                checker2 = 1
                                break
                        if checker1 == 0:  # 자음특수한 경우가 아닐때
                            checker2 = 0
                            my_word += ch
                        temp_ch = ch
                        print("1번째 ",join_jamos(my_word))
                        text_list.append(join_jamos(my_word))
                        checker1 = 0
                    elif ch in mo:  # 모음입력
                        if temp_ch == 'ㅗ' and ch in mo2:  # ㅗ였고 ㅏorㅐ이면
                            my_word = my_word[:-1]
                            temp_ch = ch
                            ch = mo4[mo2.index(ch)]
                        elif temp_ch == 'ㅜ' and ch in mo3:  # ㅜ였고 ㅓorㅔ이면
                            my_word = my_word[:-1]
                            temp_ch = ch
                            ch = mo4[mo3.index(ch) + 2]
                        else:  # 그냥 모음
                            if checker2 == 1:
                                l = my_word[-1]
                                my_word = my_word[:-1]
                                for i in range(0, 11):
                                    if jong[i][2] == l:
                                        my_word += jong[i][0]
                                        my_word += jong[i][1]
                                        break
                                temp_ch = ch
                                checker2 = 0
                            else:
                                temp_ch = ch
                        my_word += ch
                        print("2번째 ",join_jamos(my_word))
                        text_list.append(join_jamos(my_word))
                    else:  # a, b, c or d입력
                        checker2 = 0
                        if ch == 'a':
                            if temp_ch in ssang:
                                my_word = my_word[:-1]
                                my_word += chr(ord(temp_ch) + 1)
                        elif ch == 'c':
                            my_word = my_word[:-1]
                        elif ch == 'd':
                            my_word += ' '
                        print("3번째 ",join_jamos(my_word))
                        text_list.append(join_jamos(my_word))
                        temp_ch = ch
                dump_list = []
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    mean_x = hand_landmarks.landmark[0].x  # x가 왼오 0이 왼 1이 오
                    mean_y = hand_landmarks.landmark[0].y  # y가 위아래 0이 젤위 1이 젤아래
                    min_x = w - 1; max_x = 0.0; min_y = h - 1; max_y = 0.0
                    for i in range(0, 21):  # 요기부터
                        hlm = hand_landmarks.landmark[i]
                        if hlm.x * w > max_x:
                            max_x = hlm.x * w
                        if hlm.x * w < min_x:
                            min_x = hlm.x * w
                        if hlm.y * h > max_y:
                            max_y = hlm.y * h
                        if hlm.y * h < min_y:
                            min_y = hlm.y * h
                    for i in dot_list:
                        hlm = hand_landmarks.landmark[i]
                        feature_list.append(((hlm.x - mean_x) * w) / (max_x - min_x))
                        feature_list.append((hlm.y - mean_y) * h / (max_y - min_y))
                    d8 = hand_landmarks.landmark[8]
                    d12 = hand_landmarks.landmark[12]
                    d16 = hand_landmarks.landmark[16]
                    d23 = math.sqrt(pow(d8.x * w - d12.x * w, 2) + pow(d8.y * h - d12.y * h, 2))
                    d34 = math.sqrt(pow(d16.x * w - d12.x * w, 2) + pow(d16.y * h - d12.y * h, 2))
                    feature_list.append(d23 / d34 - 1)
                    #feature_list.append((max_y - min_y) / (max_x - min_x) - 1)
                    feature_list = np.round(feature_list, decimals=5)
                    feature_list = [feature_list]
                    proba = kn.predict_proba(feature_list)
                    C = my_char[np.argmax(proba[0])]
                    dump_list.append(C)
                    feature_list = []
            cv2.imshow('window', image)
            if cv2.waitKey(1) == 13:
                self.signAappend(text_list[-1])
                # 클라이언트에 text_list[-1] 전송해주기
                break


        cap.release()
        hands.close()
        cv2.destroyAllWindows()



    def handler(self, server : TCPMultiThreadServer, cSock):
        while True:
            headerBytes, dataBytesList = server.receive(cSock)
            # print(data)
            if headerBytes is None and dataBytesList is None:
                    break
            processdata = server.processData(cSock=cSock, headerBytes=headerBytes, dataBytesList=dataBytesList)

            MainWindow.messageAppend(self, processdata)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainForm = MainWindow()

    cThread = Thread(target=mainForm.handler, args=(mainForm.server, mainForm.clientSock)) # 연결된 클라이언트에 대한 쓰레드 생성
    cThread.daemon = True # 생성된 쓰레드의 데몬 여부를 True로 한다. (데몬 스레드 = 메인 스레드가 종료되면 즉시 종료되는 스레드)
    cThread.start() # 쓰레드 시작

    mainForm.show()
    sys.exit(app.exec_())

    