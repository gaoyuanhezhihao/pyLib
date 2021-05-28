import sys
sys.path = ['/home/zhihaohe/.local/lib/python3.5/site-packages/'] + sys.path
import os
import sys
import argparse
import cv2
from time import time,sleep
import threading
from player_ui import PlayerUI


def load_image(fp, dst, key, cond_var=None):
    # print("reading %s..."%fp)
    img = cv2.imread(fp)
    dst[key] = img
    if cond_var:
        cond_var.notify()
    # print("readed %s Done %d" % (fp, key))


class ImageMap:

    def __init__(self, directory):
        self.map_ = {}
        self.thread_map_ = {}
        self.i_ = 0
        self.dir_ = directory
        self.buffered_ = set()
        self.list_files(directory)
        self.update_jobs()

    def list_files(self, directory):
        fnames = os.listdir(directory)
        self.fnames_ = sorted(fnames, key=lambda x:int(x[:x.find('.')]))


    def inc(self, step = 1) :
        self.i_ += step
        self.i_ = min(self.i_, len(self.fnames_)-1)
        print(self.i_)
        self.update_jobs()

    def dec(self, step = 1):
        self.i_ -= step
        self.i_ = max(self.i_, 0)
        print(self.i_)
        self.update_jobs()


    def update_jobs(self):
        for i in range(self.i_, min(len(self.fnames_)-1, self.i_+10)):
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

    imgs = ImageMap(args.directory)
    ui = PlayerUI(imgs)
    ui.run()
