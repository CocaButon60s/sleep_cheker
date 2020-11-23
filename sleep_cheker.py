import cv2
import winsound
from datetime import datetime, timedelta
from time import sleep

# チャタ用
class Chattering():
    def __init__(self):
        self.__buf = [False, False, False]
        self.__p = 0
    
    def add(self, val):
        self.__buf[self.__p] = val
        self.__p = self.__p + 1 if self.__p + 1 < len(self.__buf) else 0

    def is_allTrue(self):
        return False not in self.__buf

move_info = Chattering()
cap = cv2.VideoCapture(0)

avg = None

def alerm():
    while True:
        winsound.Beep(440, 1000)
        k = cv2.waitKey(1000)
        if k == 27:break

start = datetime.now()
while True:
    ret, frame = cap.read()
    # フレーム取得できなかったらエラーと判断
    if not ret: break

    # グレースケールに変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 比較用フレーム取得
    if avg is None:
        avg = gray.copy().astype("float")
        continue

    # 現在のフレームと移動平均との差を計算
    cv2.accumulateWeighted(gray, avg, 0.6)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

    # デルタ画像を閾値処理を行う
    thresh = cv2.threshold(frameDelta, 15, 255, cv2.THRESH_BINARY)[1]

    cv2.imshow("thresh", thresh)

    cnt = cv2.countNonZero(thresh)
    if cnt > 500:
        move_info.add(True)
    else:
        move_info.add(False)

    now = datetime.now()
    # 動いた！
    if move_info.is_allTrue():
        # タイマ初期化
        start = datetime.now()

    # 5分以上動きがなかった
    if (now - start >= timedelta(seconds=10)):
        # 音を鳴らす
        alerm()
        sleep(3)
        # タイマ初期化
        start = datetime.now()

    # 1ms待って、Esc押されたら処理終了
    k = cv2.waitKey(500)
    if k == 27: break

cap.release()
cv2.destroyAllWindows()