import sys
sys.path = ['/home/zhihaohe/.local/lib/python3.5/site-packages/'] + sys.path
import argparse
import os
from os.path import splitext, join, split
import xml.etree.ElementTree as ET
import re
import numpy as np
import cv2

from images_player import ImageMap
from player_ui import PlayerUI

green = (0, 128, 0)
lime =(0, 255, 0)
red = (0, 0, 255)
blue = (255, 0, 0)
yellow = (51, 230, 255)

def parse_point(s):
    pt = re.findall('\d+\.*\d*', s)
    return (float(pt[0]), float(pt[1]))

def parse_line(s):
    split = s.find('--')
    start = parse_point(s[:split])
    end = parse_point(s[split+2:])
    return (start, end)

def parse_pole(line):
    split = line.find('|')
    left = line[:split]
    right = line[split+1:]
    return (parse_line(left), parse_line(right))

def parse_gt_pole(s):
    # print(s)
    floats = list(map(float, re.split(',|;', s)))
    points = [(x, y) for x, y in zip(floats[0::2], floats[1::2])]
    points = sorted(points, key=lambda p:p[1])
    top = points[:2]
    bottom = points[2:]
    top = sorted(top)
    bottom = sorted(bottom)
    return ((top[0], bottom[0]), (top[1], bottom[1]))

def parse_gt(fp):
    tree = ET.parse(fp)
    gt_map = {}
    for c in tree.getroot().getchildren():
        if 'image' == c.tag:
            poles = [parse_gt_pole(p.get('points')) for p in c.getchildren() if 'points' in p.keys()]
            name = split(c.get('name'))[-1]
            gt_map[name] = poles
    return gt_map

def area_of_bbox(bbox):
    a = (bbox[1][0] - bbox[0][0]) * (bbox[1][1] - bbox[0][1])
    assert a >= 0
    return a


def bbox_of_pole(pole):
    pts = (pole[0][0], pole[0][1], pole[1][0], pole[1][1])
    x_min = min(pole[0][0][0], pole[0][1][0])
    x_max = max(pole[1][0][0], pole[1][1][0])

    y_min = min(pole[0][0][1], pole[0][1][1])
    y_max = max(pole[1][0][1], pole[1][1][1])
    return((x_min, y_min), (x_max, y_max))

def calculate_iou_of_bbox(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle

    xA = max(boxA[0][0], boxB[0][0])
    yA = max(boxA[0][1], boxB[0][1])
    xB = min(boxA[1][0], boxB[1][0])
    yB = min(boxA[1][1], boxB[1][1])

    # compute the area of intersection rectangle
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
    if interArea == 0:
        return 0
    # compute the area of both the prediction and ground-truth
    # rectangles
    # boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    # boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(area_of_bbox(boxA)+ area_of_bbox(boxB)- interArea)

    # return the intersection over union value
    return iou


def to_point2i(pt):
    return int(pt[0]), int(pt[1])

def paint_pole(image, p, color):
    cv2.line(image, to_point2i(p[0][0]), to_point2i(p[0][1]), color, 1)
    cv2.line(image, to_point2i(p[0][1]), to_point2i(p[1][1]), color, 1)
    cv2.line(image, to_point2i(p[1][1]), to_point2i(p[1][0]), color, 1)
    cv2.line(image, to_point2i(p[1][0]), to_point2i(p[0][0]), color, 1)

class ImageIOU_Fetcher(ImageMap):

    def __init__(self, image_dir, label_dir, gt_fp):
        self.label_dir = label_dir
        self.gt_map = parse_gt(gt_fp)
        super().__init__(image_dir)
        # load gt

    def update_jobs(self):
        super().update_jobs()
        name = splitext(self.fnames_[self.i_])[0]

        print("current is %s"%self.fnames_[self.i_])
        # load labels
        label_fp = join(self.label_dir, name + '.txt')
        with open(label_fp, 'r') as f:
            detection = [parse_pole(l) for l in f.readlines()]
        # compare
        self.detected = []
        self.false_detected = []
        self.not_detected = []
        IOU_THRESHOLD = 0.5
        matched = [False for _ in detection]
        for g in self.gt_map[self.fnames_[self.i_]]:
            gt_bbox = bbox_of_pole(g)
            iou_list = [calculate_iou_of_bbox(gt_bbox , bbox_of_pole(p)) for p in detection]
            max_idx = np.argmax(iou_list)
            if iou_list[max_idx] > IOU_THRESHOLD:
                self.detected.append((g, detection[max_idx]))
                matched[max_idx] = True
            else:
                self.not_detected.append(g)
        self.false_detected = [p for m, p in zip(matched, detection) if not m]

        # paint poles to image
        image = self.map_[self.i_]
        for p, g in self.detected:
            paint_pole(image, p, green)
            paint_pole(image, g, lime)
        for p in self.false_detected:
            paint_pole(image, p, red)
        for p in self.not_detected:
            paint_pole(image, p, yellow)


    def list_files(self, d):
        fnames = os.listdir(d)
        samples = []
        for f in fnames:
            split = f.rfind('_')
            dataset_name = f[:split]
            idx = int(f[split+1: f.rfind('.')])
            samples.append((dataset_name,idx))
        samples = sorted(samples)
        print(samples)
        self.fnames_ = ["%s_%s.png" % s for s in samples]
        print("IOUViewer::list_files")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('image_directory')
    p.add_argument('label_directory')
    p.add_argument('groundtruth_path')
    args = p.parse_args()
    fetcher = ImageIOU_Fetcher(args.image_directory, args.label_directory,
                       args.groundtruth_path)
    ui = PlayerUI(fetcher)
    ui.run()

