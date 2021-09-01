import sys
sys.path = ['/home/zhihaohe/.local/lib/python3.5/site-packages/'] + sys.path
from time import time
import cv2

class PlayerUI:
    def __init__(self, image_fetcher):
        self.image_fetcher = image_fetcher

    def run(self):
        freq = 10
        pause = False
        i = 0
        while True:
            start = time()
            cv2.imshow("a", self.image_fetcher.get_image())
            e = 1000 * (time() - start)
            wait_time = 1000/freq - e
            if wait_time < 1:
                print("freq is too high")
                wait_time = 1
            cmd = cv2.waitKey(int(wait_time))
            # if -1 != cmd:
                # print(cmd)
            if cmd == 100: # 'd' next frame
                pause = True
                self.image_fetcher.inc()
            elif cmd == 97: # 'a' prev frame
                pause = True
                self.image_fetcher.dec()
            elif cmd == 44 : # ',': slow down
                freq -= 2
                freq = max(1, freq)
                print("freq=", freq)
            elif cmd == 46: # '.': speed up
                freq += 2
                print("freq=", freq)
            elif cmd == 32: #space: toggle pause/play
                pause = not pause
            elif cmd == 113: # q: quit
                print("exit")
                break
            if not pause:
                self.image_fetcher.inc()
