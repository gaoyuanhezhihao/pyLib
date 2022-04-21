from logger import logger, timed
import sys
import os
from os.path import join
import sys
import argparse
import cv2
from time import time,sleep
from timeit import default_timer as timer
import threading
from player_ui import PlayerUI
from thread_pool import ThreadPool
from functools import partial
import glob
import re
from ssd_cache import DirectoryCache, _1GB, Job
from threading import Lock
PROFILE_MODE=True
if PROFILE_MODE:
    from viztracer import VizTracer

# import ipdb


# def load_image(fp, dst, key, color_scale):
    # # print("reading %s..."%fp)
    # assert os.path.exists(fp), fp
    # img = cv2.imread(fp)
    # if color_scale:
        # img = img * color_scale
    # dst[key] = img
    # # if cond_var:
        # # cond_var.notify()
    # # print("readed %s Done %d" % (fp, key))

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

def list_images(args):
    file_paths = []
    if args.load_cached_file_list and load_cached_file_list(args.directory+args.extension, file_paths):
        print('load cached files')
    else:
        fnames = os.listdir(args.directory)
        fnames = [f for f in fnames if f.endswith(args.extension)]
        fnames = sorted(fnames)
        file_paths = [join(args, directory, fname) for fname in fnames]

    if args.cache_file_list:
        cache_file_list(args.directory + args.extension, file_paths)
    return file_paths


def glob_images(args):
    file_paths = []
    file_list_id = args.pattern.replace('*', '_star_')
    file_list_id = file_list_id.replace('/', '_')
    if args.load_cached_file_list and load_cached_file_list(file_list_id, file_paths):
        print('load cached files')
    else:
        file_paths = glob.glob(args.pattern)
        if args.cache_file_list:
            cache_file_list(file_list_id, file_paths)
    return file_paths




class ImageMap:

    def __init__(self, file_paths, color_scale=None, start_index=0):
        if len(file_paths) == 0:
            print('Error: no files loaded')
            exit(-1)
        self.thread_number = 4
        self.prefetch_number = 8
        self.map_lock = Lock()
        self.map_ = {}
        self.thread_map_ = {}
        self.i_ = start_index
        self.buffer_lock = Lock()
        self.buffered_ = set()
        self.file_paths = file_paths
        self.thread_pool = ThreadPool(self.thread_number)
        self.color_scale = color_scale
        self.cache = DirectoryCache(_1GB, file_paths)
        # self.update_jobs()

    def inc(self, step=1):
        self.i_ += step
        self.i_ = min(self.i_, len(self.file_paths)-1)
        if step > 50:
            self.cache.reset_prefetch_jobs(self.i_)
        logger.info('inc %s', self.file_paths[self.i_])
        # print('inc:', self.file_paths[self.i_])
        self.update_jobs()

    def dec(self, step=1):
        self.i_ -= step
        self.i_ = max(self.i_, 0)
        if step > 50:
            self.cache.reset_prefetch_jobs(self.i_)
        logger.info('dec %s', self.file_paths[self.i_])
        # print('dec:', self.file_paths[self.i_])
        self.update_jobs()


    @timed
    def update_jobs(self):
        for i in range(self.i_, min(len(self.file_paths), self.i_+self.prefetch_number)):
            if i not in self.map_:
                job = Job(partial(self.__load_image, i))
                self.map_[i] = job
                self.thread_pool.add_job(job)

    @timed
    def clear_old_buffer(self):
        old_ids = []
        with self.buffer_lock:
            old_ids = [i for i in self.buffered_ if i < self.i_ - 5]
        for i in old_ids:
            with self.map_lock:
                old_img = self.map_.pop(i)
            del old_img
            with self.buffer_lock:
                self.buffered_.remove(i)

    @timed
    def __add_to_map(self, img, i):
        with self.buffer_lock:
            self.buffered_.add(i)
        with self.map_lock:
            self.map_[i] = img

    @timed
    def __load_image(self, i):
        logger.info('__load_image %d', i)
        assert i not in self.map_ or isinstance(self.map_[i], Job)
        cache_path = self.cache.get_cache_path(i)
        assert os.path.exists(cache_path)
        img = cv2.imread(cache_path)
        assert img is not None
        if self.color_scale:
            img = img * self.color_scale
        self.__add_to_map(img, i)

    @timed
    def get_image(self):
        # start = time()
        # assert self.i_ in self.map_, 'Invalid key %d, only follow keys in map:%s' % (self.i_, ','.join(self.map_.keys()))
        # while type(self.map_[self.i_]) == int:
            # sleep(0.001)
        # print('waited %f ms' % (time() - start) * 1000)
        # return self.map_[self.i_]
        logger.info('get_image %d', self.i_)
        if self.i_ not in self.map_:
            self.__load_image(self.i_)
        else:
            logger.info('wait on job')
            record = self.map_[self.i_]
            if isinstance(record, Job):
                record.wait()
        self.clear_old_buffer()
        return self.map_[self.i_]


    def stop(self):
        self.thread_pool.stop()
        self.cache.__exit__()


def cache_file_list(file_list_id, file_lists):
    print('cache_file_list')
    CACHE_DIR = './cached_file_lists/'
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(join(CACHE_DIR, file_list_id+'.txt'), 'w') as f:
        print(f.name)
        f.write('\n'.join(file_lists))


def load_cached_file_list(file_list_id, image_files):
    CACHE_DIR = './cached_file_lists/'
    cache_file_path = join(CACHE_DIR, file_list_id+'.txt')
    if os.path.exists(cache_file_path):
        print('use cahced file lists')
        with open(cache_file_path, 'r') as f:
            for l in f.readlines():
                image_files.append(l)
        return True
    else:
        print('no cache records:', cache_file_path)
        return False




if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--pattern')
    p.add_argument('--directory')
    p.add_argument('--cache_file_list', type=bool, default=False, help='For files on NFS, it cost much time to list directory or glob, cache them and reuse next time could speed up the loading period')
    p.add_argument('--load_cached_file_list', type=bool, default=True)
    p.add_argument('--extension', dest='extension', default='jpg', help='extension of image files')
    p.add_argument('--color_scale', type=int, default=None, help='color scale will be multiplied to every r,g,b of every pixel')
    p.add_argument('--start_timestamp', type=float, help='start from frame whose timestamp is first one larger than this timestamp')
    args = p.parse_args()


    # fnames = os.listdir(args.directory)
    # fnames = sorted(fnames, key=lambda x:int(x[:x.find('.')]))

    image_files = []
    if args.directory:
        image_files = list_images(args)
    elif args.pattern:
        image_files = glob_images(args)

    start_index = 0
    if args.start_timestamp:
        p = re.compile(r'\d*\.\d*')
        for i in range(len(image_files)):
            m = p.findall(image_files[i])
            if m and float(m[0]) > args.start_timestamp:
                start_index = i
                break

    if PROFILE_MODE:
        tracer = VizTracer()
        tracer.start()
    image_fetcher = ImageMap(image_files, args.color_scale, start_index=start_index)
    ui = PlayerUI(image_fetcher)
    ui.run()
    if PROFILE_MODE:
        tracer.stop()
        tracer.save()
    image_fetcher.stop()
