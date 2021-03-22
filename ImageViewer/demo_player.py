import sys
sys.path = ['/home/zhihaohe/.local/lib/python3.5/site-packages/'] + sys.path
from images_player import ImageMap
import argparse
from time import time

p = argparse.ArgumentParser()
p.add_argument('directory')
args = p.parse_args()


a = ImageMap(args.directory)

for _ in range(10):
    start = time()
    a.get_image()
    print('waited ' , (time() - start) * 1000)
    a.inc()
