import pytest
import os
from os.path import join
from ssd_cache import LRU
import ssd_cache
import shutil
from random import randint
import time


def test_LRU_remove_old():
    d = '/tmp/unittest_ssd_cache/'
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    for i in range(4):
        with open(join(d, str(i)), 'wb') as f:
            f.truncate(1024)
    lru = LRU(d, 3 * 1024)
    lru.remove_old()
    assert set([f for f in os.listdir(d)]) == set(['1', '2', '3'])


def prepare_dir(src_dir, cache_dir):
    if os.path.exists(src_dir):
        shutil.rmtree(src_dir)
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(src_dir)
    os.makedirs(cache_dir)


def prepare_src(src_dir, cnt=4):
    for i in range(cnt):
        with open(join(src_dir, str(i)), 'wb') as file:
            file.truncate(1024)


def test_LRU_create():
    src_dir = '/tmp/unittest_ssd_cache/src/'
    cache_dir = '/tmp/unittest_ssd_cache/dest/'
    prepare_dir(src_dir, cache_dir)
    prepare_src(src_dir)
    lru = LRU(cache_dir, 3 * 1024)
    for i in range(4):
        cache_fp = lru.get(join(src_dir, str(i)))
        assert cache_fp == join(cache_dir, str(i))
    lru.remove_old()
    assert set([f for f in os.listdir(cache_dir)]) == set(['1', '2', '3'])
    lru.__exit__()

def test_LRU_update():
    src_dir = '/tmp/unittest_ssd_cache/src/'
    cache_dir = '/tmp/unittest_ssd_cache/dest/'
    prepare_dir(src_dir, cache_dir)
    prepare_src(src_dir)
    lru = LRU(cache_dir, 3 * 1024)
    for i in range(4):
        cache_fp = lru.get(join(src_dir, str(i)))
    lru.get(join(src_dir, str(0)))
    lru.remove_old()
    assert set([f for f in os.listdir(cache_dir)]) == set(['0', '2', '3'])


def test_LRU_update2():
    src_dir = '/tmp/unittest_ssd_cache/src/'
    cache_dir = '/tmp/unittest_ssd_cache/dest/'
    prepare_dir(src_dir, cache_dir)
    prepare_src(src_dir)
    lru = LRU(cache_dir, 3 * 1024)
    for i in range(4):
        lru.get(join(src_dir, str(i)))
    for _ in range(100):
        lru.get(join(src_dir, str(randint(0, 3))))
    lru.get(join(src_dir, str(0)))
    lru.get(join(src_dir, str(1)))
    lru.get(join(src_dir, str(3)))
    lru.remove_old()
    cached_files= set([f for f in os.listdir(cache_dir)])
    assert cached_files == set(['0', '1', '3']), cached_files


def test_LRU_update3():
    src_dir = '/tmp/unittest_ssd_cache/src/'
    cache_dir = '/tmp/unittest_ssd_cache/dest/'
    prepare_dir(src_dir, cache_dir)
    prepare_src(src_dir)
    lru = LRU(cache_dir, 3 * 1024)
    for i in range(4):
        lru.get(join(src_dir, str(i)))
    for _ in range(100):
        lru.get(join(src_dir, str(randint(0, 3))))
    lru.remove_old()
    lru.get(join(src_dir, str(0)))
    lru.get(join(src_dir, str(1)))
    lru.get(join(src_dir, str(3)))
    assert set([f for f in os.listdir(cache_dir)]) == set(['0', '1', '3'])

_1KB = 1024
_1MB = 1024 * _1KB
_1GB = 1024 * _1MB


def test_DirectoryCache():
    src_dir = '/tmp/unittest_ssd_cache/src/'
    cache_dir = '/tmp/_tmp_unittest_ssd_cache_src/'
    prepare_dir(src_dir, cache_dir)
    prepare_src(src_dir, 1000)
    ssd_cache.TAIL_THRES = 10
    ssd_cache.HEAD_THRES = 5
    ssd_cache.PREV_FETCH = 10
    ssd_cache.AFTER_FETCH = 20
    # src_paths = [join(src_dir, f) for f in os.listdir(src_dir)]
    src_paths = [join(src_dir, str(i)) for i in range(1000)]
    cache = ssd_cache.DirectoryCache(512 * _1KB, src_paths)
    time_used_sum = 0.0
    try:
        for i in range(1000):
            start = time.time()
            cache_path = cache.get_cache_path(i)
            time_used_sum += time.time() - start
            assert os.path.split(src_paths[i])[1] == os.path.split(cache_path)[1]
    except Exception as e:
        cache.__exit__()
        raise e
    finally:
        cache.__exit__()
    print('time used average ', time_used_sum / 1000)

if __name__ == '__main__':
    test_LRU_update2()
    # test_DirectoryCache()
