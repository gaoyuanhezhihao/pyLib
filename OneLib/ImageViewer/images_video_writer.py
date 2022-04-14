import cv2
import os
import argparse
import glob
from tqdm import tqdm
import re


parser = argparse.ArgumentParser()
parser.add_argument("--images_pattern", type=str)
parser.add_argument("--video_path", type=str, default="./video.avi")
parser.add_argument("--color_scale", type=int, default=1)
parser.add_argument("--length", type=int, default=-1)
args = parser.parse_args()


def list_timed_files(pattern):
    files = glob.glob(pattern)
    p = re.compile(r'\d+\.\d+')
    items = [(float(re.search(p, f).group()), f) for f in files if re.search(p, f)]
    sorted_items = sorted(items)
    return [f[1] for f in sorted_items]


images_file_paths = list_timed_files(args.images_pattern)
if args.length != -1:
    images_file_paths = images_file_paths[:args.length]
# print(images_file_paths)
if len(images_file_paths) == 0:
    print('Error, no image')
    exit(-1)
first_frame = cv2.imread(images_file_paths[0])
height, width, layers = first_frame.shape

video = cv2.VideoWriter(args.video_path, cv2.VideoWriter.fourcc(*"MJPG"), 5, (width, height))

for image_file_path in tqdm(images_file_paths):
    video.write(cv2.imread(image_file_path) * args.color_scale)

video.release()
