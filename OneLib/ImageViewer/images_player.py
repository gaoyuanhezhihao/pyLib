import sys
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
import glob
import re


def load_image(fp, dst, key, color_scale):
    # print("reading %s..."%fp)
    assert os.path.exists(fp), fp
    img = cv2.imread(fp)
    if color_scale:
        img = img * color_scale
    dst[key] = img
    # if cond_var:
        # cond_var.notify()
    # print("readed %s Done %d" % (fp, key))

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def list_first_file_of_subdirectories(directory):
    TARGET_FILE = "point_association_1.png"
    file_paths = []
    for name in os.listdir(directory):
        if os.path.isdir(join(directory, name)) and isfloat(name):
            fp = join(directory, name, TARGET_FILE)
            if os.path.exists(fp):
                file_paths.append(fp)
                assert os.path.exists(fp)
    return sorted(file_paths, key=lambda x:float(x.split('/')[-2]))

def list_float_timed_files(directory, extension):
    fnames = os.listdir(directory)
    fnames = [f for f in fnames if f.endswith(extension)]
    fnames = sorted(fnames, key=lambda x:float(x[:x.rfind('.')]))
    return [join(directory, fname) for fname in fnames]

def list_timed_files(pattern):
    files = glob.glob(pattern)
    p = re.compile(r'\d*\.\d*')
    items = [float(re.search(p, f).group()) for f in files if re.search(p, f)]
    sorted_items = sorted(items)
    return [f[1] for f in sorted_items]

def list_images(directory, extension):
    fnames = os.listdir(directory)
    fnames = [f for f in fnames if f.endswith(extension)]
    fnames = sorted(fnames)
    return [join(directory, fname) for fname in fnames]


class ImageMap:

    def __init__(self, file_paths, color_scale=None):
        if len(file_paths) == 0:
            print('Error: no files loaded')
            exit(-1)
        self.prefetch_number = 8
        self.map_ = {}
        self.thread_map_ = {}
        self.i_ = 0
        self.buffered_ = set()
        self.file_paths= file_paths
        self.thread_pool = ThreadPool(self.prefetch_number)
        self.color_scale = color_scale
        self.update_jobs()

    def inc(self, step=1):
        self.i_ += step
        self.i_ = min(self.i_, len(self.file_paths)-1)
        print('inc:', self.file_paths[self.i_])
        self.update_jobs()

    def dec(self, step=1):
        self.i_ -= step
        self.i_ = max(self.i_, 0)
        print('dec:', self.file_paths[self.i_])
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
        assert self.i_ in self.map_, 'Invalid key %d, only follow keys in map:%s' % (self.i_, ','.join(self.map_.keys()))
        while type(self.map_[self.i_]) == int:
            sleep(0.001)
        # print('waited %f ms' % (time() - start) * 1000)
        return self.map_[self.i_]

    def stop(self):
        self.thread_pool.stop()



if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--pattern')
    p.add_argument('--directory')
    p.add_argument('--extension', dest='extension', default='jpg', help='extension of image files')
    p.add_argument('--color_scale', type=int, default=None, help='color scale will be multiplied to every r,g,b of every pixel')
    args = p.parse_args()


    # fnames = os.listdir(args.directory)
    # fnames = sorted(fnames, key=lambda x:int(x[:x.find('.')]))

    image_files = []
    if args.directory:
        image_files = list_images(args.directory, args.extension)
    elif args.pattern:
        print("use glob pattern")
    image_fetcher = ImageMap(image_files, args.color_scale)
    image_fetcher = ImageMap(image_files)
    ui = PlayerUI(image_fetcher)
    ui.run()
    image_fetcher.stop()
