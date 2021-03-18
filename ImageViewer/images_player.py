import sys
sys.path = ['/home/zhihaohe/.local/lib/python3.5/site-packages/'] + sys.path
import os
import sys
import argparse
import cv2
from time import time,sleep
import threading


def load_image(fp, dst, key, cond_var=None):
    print("reading %s..."%fp)
    img = cv2.imread(fp)
    dst[key] = img
    if cond_var:
        cond_var.notify()
    print("readed %s Done %d" % (fp, key))


class ImageMap:

    def __init__(self, directory):
        self.map_ = {}
        self.thread_map_ = {}
        self.i_ = 0
        self.dir_ = directory
        fnames = os.listdir(directory)
        self.fnames_ = sorted(fnames, key=lambda x:int(x[:x.find('.')]))
        self.buffered_ = set()
        self.update_jobs()

    def inc(self, step = 1) :
        self.i_ += step
        self.i_ = min(self.i_, len(self.fnames_)-1)
        self.update_jobs()

    def dec(self, step = 1):
        self.i_ -= step
        self.i_ = max(self.i_, 0)
        self.update_jobs()


    def update_jobs(self):
        for i in range(self.i_, self.i_+10):
            if i not in self.map_:
                self.buffered_.add(i)
                self.map_[i] = i
                fp = os.path.join(self.dir_, self.fnames_[i])
                self.thread_map_[i] = threading.Thread(target=load_image, args=(fp, self.map_, i))
                self.thread_map_[i].start()

        # remove too old image
        old_ids = []
        for i in self.buffered_:
            if i < self.i_ - 5:
                self.map_.pop(i)
                old_ids.append(i)
        for i in old_ids:
            self.buffered_.remove(i)

    def get_image(self):
        # start = time()
        while type(self.map_[self.i_]) == int:
            sleep(0.001)
        # print('waited %f ms' % (time() - start) * 1000)
        return self.map_[self.i_]


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('directory')
    args = p.parse_args()


    fnames = os.listdir(args.directory)
    fnames = sorted(fnames, key=lambda x:int(x[:x.find('.')]))

    freq = 10
    stop = False
    i = 0
    imgs = ImageMap(args.directory)

    while i < len(fnames):
        start = time()
        # f = fnames[i]
        # img = cv2.imread(os.path.join(args.directory, f))
        cv2.imshow("a", imgs.get_image())
        # cmd = cv2.waitKey(1000/speed)
        e = 1000 * (time() - start)
        wait_time = 1000/freq - e
        if wait_time < 1:
            print("freq is too high")
            wait_time = 1
        cmd = cv2.waitKey(int(wait_time))
        # print(type(cmd))
        # print(cmd)
        # exit()
        if cmd == 83: # -> next frame
            stop = True
            imgs.inc()
            # i += 1
        elif cmd == 81: # <-- prev frame
            stop = True
            imgs.dec()
            # i -= 1
        elif cmd == 97: # a: slow down
            freq -= 2
            freq = max(1, freq)
            print("freq=", freq)
        elif cmd == 100: # d: speed up
            freq += 2
            print("freq=", freq)
        elif cmd == 32: #space: toggle pause/play
            stop = not stop
        elif cmd == 113: # q: quit
            exit(0)
        if not stop:
            imgs.inc()
            # i += 1
