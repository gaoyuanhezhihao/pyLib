import sys
sys.path = ['/home/zhihaohe/.local/lib/python3.5/site-packages/'] + sys.path
import os
from os.path import join
import sys
import argparse
import cv2
from time import time,sleep
import threading
from player_ui import PlayerUI
from thread_pool import ThreadPool
from functools import partial


def load_image(fp, dst, key, cond_var=None):
    # print("reading %s..."%fp)
    assert os.path.exists(fp)
    img = cv2.imread(fp)
    dst[key] = img
    if cond_var:
        cond_var.notify()
    # print("readed %s Done %d" % (fp, key))

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def list_first_file_of_subdirectories(directory):
    TARGET_FILE = "point_association_1.bmp"
    file_paths = []
    for name in os.listdir(directory):
        if os.path.isdir(join(directory, name)) and isfloat(name):
            fp = join(directory, name, TARGET_FILE)
            if os.path.exists(fp):
                file_paths.append(fp)
    return sorted(file_paths, key=lambda x:float(x.split('/')[-2]))


class ImageMap:

    def __init__(self, directory, list_file_func=None):
        self.prefetch_number = 8
        self.map_ = {}
        self.thread_map_ = {}
        self.i_ = 0
        self.dir_ = directory
        self.buffered_ = set()
        if list_file_func:
            self.file_paths= list_file_func(directory)
        else:
            self.file_paths = self.list_files(directory)
        self.thread_pool = ThreadPool(self.prefetch_number)
        self.update_jobs()

    def list_files(self, directory):
        fnames = os.listdir(directory)
        fnames = sorted(fnames, key=lambda x:int(x[:x.find('.')]))
        return [join(directory, fname) for fname in fnames]


    def inc(self, step = 1) :
        self.i_ += step
        self.i_ = min(self.i_, len(self.file_paths)-1)
        print(self.file_paths[self.i_])
        self.update_jobs()

    def dec(self, step = 1):
        self.i_ -= step
        self.i_ = max(self.i_, 0)
        print(self.file_paths[self.i_])
        self.update_jobs()


    def update_jobs(self):
        for i in range(self.i_, min(len(self.file_paths), self.i_+self.prefetch_number)):
            if i not in self.map_:
                self.buffered_.add(i)
                self.map_[i] = i
                self.thread_pool.add_job(partial(load_image, self.file_paths[i], self.map_, i))

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

    def stop(self):
        self.thread_pool.stop()



if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('directory')
    args = p.parse_args()


    # fnames = os.listdir(args.directory)
    # fnames = sorted(fnames, key=lambda x:int(x[:x.find('.')]))

    image_fetcher = ImageMap(args.directory, list_first_file_of_subdirectories)
    ui = PlayerUI(image_fetcher)
    ui.run()
    image_fetcher.stop()
