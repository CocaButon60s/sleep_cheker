import cv2
import winsound
import subprocess
from datetime import datetime, timedelta
from time import sleep

# チャタ用
class History():
    def __init__(self):
        self.__buf = [False, False, False]
        self.__p = 0
    def add(self, val):
        self.__buf[self.__p] = val
        self.__p = self.__p + 1 if self.__p + 1 < len(self.__buf) else 0
    def is_allTrue(self): return False not in self.__buf

# 経過時間管理
class TimeMng():
    def __init__(self): self.__start = None
    def update(self): self.__start = datetime.now()
    def get_timedelta(self, now: datetime) -> timedelta: return now - self.__start
    def is_over(self, now: datetime) -> bool:
        # 5分以上動きがなかった
        if (now - self.__start >= timedelta(minutes=5)): return True
        return False

def alerm(f):
    # 音量調整
    subprocess.call("tools\Volume.ps1", shell=True)
    while True:
        winsound.Beep(f, 1000)
        k = cv2.waitKey(1000)
        # Esc押されたら処理終了
        if k == 27: break
    sleep(3)

def main():
    move_info = History()
    timer = TimeMng()
    cap = cv2.VideoCapture(0)
    avg = None

    timer.update()
    while True:
        ret, frame = cap.read()
        # フレーム取得できなかったらエラーと判断
        if not ret:
            cap = cv2.VideoCapture(0)
            continue

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
        if cnt > 500: move_info.add(True)
        else: move_info.add(False)

        now = datetime.now()
        # 動いた！
        if move_info.is_allTrue():
            # タイマ初期化
            print(timer.get_timedelta(now))
            timer.update()

        # 5分以上動きがなかった
        if timer.is_over(now):
            print(timer.get_timedelta(now))
            # 音を鳴らす
            alerm(440)
            # タイマ初期化
            timer.update()

        # Esc押されたら処理終了
        k = cv2.waitKey(500)
        if k == 27: break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__": main()