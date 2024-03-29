import os
from logger import logger, timed
from os.path import join
from functools import partial
import cv2
import shutil
# from collections import deque
from threading import Condition
import multiprocessing as mp
import queue
from thread_pool import ThreadPool
import logging
from threading import Lock
import time
from linked_list import LinkedList
from datetime import datetime
# import atexit

HEAD_THRES = 5
TAIL_THRES = 200

PREV_FETCH =  2 * HEAD_THRES
AFTER_FETCH = 2 * TAIL_THRES

# logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                    # level=logging.INFO,
                    # datefmt='%H:%M:%S')

# logger = logging.getLogger('DirectoryCache')
# handler = logging.FileHandler('DirectoryCache%s.log' % datetime.now().ctime().replace(' ', '_'))
# handler.setLevel(logging.INFO)
# logger.addHandler(handler)

def copy_file(src_path, dest_path):
    # time.sleep(1)
    shutil.copyfile(src_path, dest_path)

class Job:
    def __init__(self, func):
        self.func = func
        self.cond = Condition()
        self.completed = False

    def __call__(self):
        ret = self.func()
        self.complete()
        return ret

    def complete(self):
        with self.cond:
            self.completed = True
            self.cond.notify()

    def is_completed(self):
        return self.completed

    def wait(self):
        with self.cond:
            self.cond.wait_for(self.is_completed)
        assert self.completed


# class LRU_SLOT:

    # def __init__(self, src_path):

class LRU:

    def __init__(self, cache_directory, max_disk_bytes):
        self.max_disk_bytes = max_disk_bytes
        self.directory_space_costed = 0
        self.cache_directory = cache_directory
        self.lock = Lock()
        logger = logging.getLogger('LRU')
        self.__load__cache__()
        self.thread_pool = ThreadPool(32)

    def __load__cache__(self):
        file_names = [f for f in os.listdir(self.cache_directory) if not os.path.isdir(f)]
        file_paths = [join(self.cache_directory, fn) for fn in file_names]
        for fp in file_paths:
            self.directory_space_costed += os.path.getsize(fp)
        cache_records = sorted([(os.path.getmtime(fp), fn) for fp, fn in zip(file_paths, file_names)])
        self.cache_priority_list = LinkedList()
        self.fname_to_record_id_map = {}
        for record in cache_records:
            record_node = self.cache_priority_list.push_back(record)
            self.fname_to_record_id_map[record[1]] = record_node


    def __exit__(self):
        self.thread_pool.stop()

    @timed
    def get(self, src_path):
        logger.info('get %s', src_path)
        src_directory, fname = os.path.split(src_path)
        if fname in self.fname_to_record_id_map:
            return self.__get_from_cache(src_path)
        else:
            with self.lock:
                logger.info('create job for %s', fname)
                job = Job(partial(self.__create, src_path))
                self.fname_to_record_id_map[fname] = job
            return job()

    @timed
    def __get_from_cache(self, src_path):
        src_directory, fname = os.path.split(src_path)
        logger.info('get from cache %s', fname)
        record = self.fname_to_record_id_map[fname]
        if type(record) == Job:
            logger.info('wait for complete %s', fname)
            record.wait()
            if type(self.fname_to_record_id_map[fname]) == Job:
                logger.warning('Job pre-finished: %s', fname)
                return self.__create(src_path)
        return self.__touch(fname)


    @timed
    def __touch(self, fname):
        logger.info('touch %s', fname)
        cache_file_path = join(self.cache_directory, fname)
        assert os.path.exists(cache_file_path)
        file_path = join(self.cache_directory, fname)
        os.utime(file_path) # touch file
        with self.lock:
            old_record_node = self.fname_to_record_id_map[fname]
            self.cache_priority_list.erase(old_record_node)
            new_record_node = self.cache_priority_list.push_back((os.path.getmtime(file_path), fname))
            self.fname_to_record_id_map[fname] = new_record_node
            # self.fname_to_record_id_map[fname] = len(self.cache_records) - 1
            # self.cache_records[old_index] = None
            assert not self.cache_priority_list.empty()
        return cache_file_path

    @timed
    def prefetch(self, src_path):
        src_directory, fname = os.path.split(src_path)
        if fname in self.fname_to_record_id_map:
            logger.info('already fetched of fetching %s', fname)
        else:
            with self.lock:
                if fname not in self.fname_to_record_id_map:
                    cache_file_path = join(self.cache_directory, fname)
                    assert not os.path.exists(cache_file_path), cache_file_path
                    logger.info('create job for %s', fname)
                    job = Job(partial(self.__create, src_path))
                    self.fname_to_record_id_map[fname] = job
                    self.thread_pool.add_job(job)

    def clear_job_queue(self):
        self.thread_pool.clear_job_queue()


    @timed
    def __create(self, src_path):
        src_directory, fname = os.path.split(src_path)
        logger.info('creating %s', fname)
        cache_file_path = join(self.cache_directory, fname)
        assert not os.path.exists(cache_file_path), cache_file_path
        assert os.path.exists(src_path), "file not exits:'%s'"%src_path
        assert fname not in self.fname_to_record_id_map or type(self.fname_to_record_id_map[fname]) == Job
        copy_file(src_path, cache_file_path)
        # shutil.copyfile(src_path, cache_file_path)
        os.utime(cache_file_path)
        file_size = os.path.getsize(cache_file_path)
        with self.lock:
            node = self.cache_priority_list.push_back((os.path.getmtime(cache_file_path), fname))
            assert not self.cache_priority_list.empty()
            self.fname_to_record_id_map[fname] = node
            self.directory_space_costed += file_size
        logger.info('created %s', fname)
        return cache_file_path

    def remove_old(self):
        # logger.info('disk size:%d', self.directory_space_costed)
        # logger.info(self.cache_priority_list.empty())
        while self.directory_space_costed > self.max_disk_bytes and not self.cache_priority_list.empty():
            with self.lock:
                oldest_record = self.cache_priority_list.head()
                self.cache_priority_list.erase(oldest_record)
                self.fname_to_record_id_map.pop(oldest_record.data[1])
            cache_path = join(self.cache_directory, oldest_record.data[1])
            assert os.path.exists(cache_path)
            self.directory_space_costed -= os.path.getsize(cache_path)
            os.remove(cache_path)
            logger.info('remove %s', cache_path)


class DirectoryCache:

    def __init__(self, max_disk_size, src_path_list):
        self.src_path_list = [p.strip() for p in src_path_list]
        self.src_directory = os.path.split(src_path_list[0])[0]
        directory_id = self.replace_path_to_id(self.src_directory)
        cache_root_dir = '/tmp'
        self.max_disk_size = max_disk_size
        self.cache_dir = join(cache_root_dir, directory_id)
        os.makedirs(self.cache_dir, exist_ok=True)
        self.lru = LRU(self.cache_dir, self.max_disk_size)
        self.prefetch_head = 0
        self.prefetch_end = 0
        self.last_prefetch_update_index = -10000
        # self.thread_pool = ThreadPool(16)
        # atexit.register(self.__exit__)

    def __exit__(self):
        self.lru.__exit__()

    @timed
    def update_prefetch_jobs(self, i):
        if i - self.last_prefetch_update_index > TAIL_THRES or self.last_prefetch_update_index - i > HEAD_THRES:
            self.last_prefetch_update_index = i
            # add new jobs
            self.prefetch_head = max(0, i - PREV_FETCH)
            self.prefetch_end = min(len(self.src_path_list), i + AFTER_FETCH)
            logger.info('refesh prefetch jobs: [%d, %d]', self.prefetch_head, self.prefetch_end)
            for k in range(i, self.prefetch_end):
                self.lru.prefetch(self.src_path_list[k])
            for k in range(self.prefetch_head, i):
                self.lru.prefetch(self.src_path_list[k])

    def replace_path_to_id(self, path):
        id_str = path.replace('*', '_star_')
        id_str = id_str .replace('/', '_')
        return id_str

    # def prefetch(self, path):
        # directory, fname = os.path.split(path)
        # assert directory == self.src_directory
        # directory_id = self.replace_path_to_id(directory)
        # cache_dir = join(self.cache_root_dir, directory_id)
        # directory_to_lru_caches[directory] = LRU(cache_dir, self.max_disk_size)
        # os.makedirs(cache_root_dir, exist_ok=True)
        # cache_file_path = join(cache_root_dir, fname)
        # if not os.path.exists(cache_file_path):
            # shutil.copyfile(path, cache_file_path)
        # return self.lru.get(path)

    def reset_prefetch_jobs(self, i):
        logger.info('reset prefetch job to %d', i)
        self.lru.clear_job_queue()
        self.update_prefetch_jobs(i)

    def get_cache_path(self, index):
        logger.info('get_cache_path %d', index)
        cache_path = self.lru.get(self.src_path_list[index])
        self.update_prefetch_jobs(index)
        self.lru.remove_old()
        return cache_path

_1KB = 1024
_1MB = 1024 * _1KB
_1GB = 1024 * _1MB


def cacher_main(request_queue, cache_path_queue, shutdown_event, src_path_list):
    cacher = DirectoryCache(_1GB, src_path_list)
    while not shutdown_event.is_set():
        try:
            item = request_queue.get(block=True, timeout=0.1)
        except queue.Empty:
            continue
        if item == 'END':
            break
        else:
            assert type(item) == int, item
            cache_fp = cacher.get_cache_path(item)
            cache_path_queue.put(cache_fp)
            cacher.update_prefetch_jobs(item)

class Client:
    def __init__(self, src_path_list):
        mp.set_start_method('spawn')
        self.shutdown_event = mp.Event()
        self.request_queue = mp.Queue()
        self.cache_path_queue = mp.Queue()
        self.process = mp.Process(target=cacher_main, args=(self.request_queue, self.cache_path_queue, self.shutdown_event, src_path_list))
        self.process.start()

    def get(self, index):
        self.request_queue.put(index)
        return self.cache_path_queue.get()
