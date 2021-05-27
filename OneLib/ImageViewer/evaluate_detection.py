import argparse
import os
from os.path import split,join,splitext
import xml.etree.ElementTree as ET
import re
import numpy as np
from shapely.geometry import Polygon
from debug_tool import paint_polygons
from matplotlib import pyplot as plt



def parse_point(s):
    s.split(',')
    _, p1, p2, _ = re.split(',|\\(|\\)', s)
    # pt = re.findall('\d+\.*\d*', s)
    return (float(p1), float(p2))

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
            name = splitext(name)[0]
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

def polygon_of_pole(pole):
    assert pole[0][0][1] < pole[0][1][1], pole
    assert pole[1][0][1] < pole[1][1][1], pole
    points = [pole[0][0], pole[0][1], pole[1][1], pole[1][0]]
    return Polygon(points)


def calculate_iou_of_poles(pole_a, pole_b):
    polygon_a = polygon_of_pole(pole_a)
    polygon_b = polygon_of_pole(pole_b)
    # print(polygon_a)
    # print(polygon_b)
    try:
        intersection = polygon_a.intersection(polygon_b)
    except Exception as e:
        print(e)
        # paint_polygons(polygon_a, polygon_b)
        # plt.show()
        return 0.0
    else:
        # print(intersection)
        return intersection.area/ (polygon_a.area + polygon_b.area - intersection.area)

def calculate_iou_of_bbox(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0][0], boxB[0][0])
    yA = max(boxA[0][1], boxB[0][1])
    xB = min(boxA[1][0], boxB[1][0])
    yB = min(boxA[1][1], boxB[1][1])

    # compute the area of intersection rectangle
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
    # print("intersection area=", interArea)
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


IOU_THRESHOLD = 0.5
EPS = 1e-9



def compare_with_groundtruth(detected_poles, ground_truth):
    true_detection = []
    not_detected = []
    matched = [False] * len(detected_poles)
    for g in ground_truth:
        iou_list = [calculate_iou_of_poles(g, p) for p in detected_poles]
        max_idx = np.argmax(iou_list)
        if iou_list[max_idx] > IOU_THRESHOLD:
            true_detection.append((g, detected_poles[max_idx]))
            matched[max_idx] = True
        else:
            not_detected.append(g)
    false_detection = [p for m, p in zip(matched, detected_poles) if not m]
    return true_detection, false_detection, not_detected

class DetectionEvaluator:

    def __init__(self, gt_fp, detection_directory):
        self.gt_map = parse_gt(gt_fp)
        self.detection_map = {}
        for file_name in os.listdir(detection_directory):
            if not file_name.endswith('.txt'):
                continue
            self.evaluate(join(detection_directory, file_name))

    def __getitem__(self, key):
        return self.detection_map[key]

    def evaluate(self, detection_file_path):
        sample_name = splitext(split(detection_file_path)[-1])[0]
        with open(detection_file_path, 'r') as f:
            detected_poles = [parse_pole(l) for l in f.readlines()]
            # print("detected %d poles in %s" % (len(detected_poles), file_name))
            true_detection = []
            false_detection = []
            ground_truth = self.gt_map[sample_name]
            not_detected = ground_truth
            if len(detected_poles) != 0:
                true_detection, false_detection, not_detected = compare_with_groundtruth(detected_poles, ground_truth)
            self.detection_map[sample_name] = {'true_detection': true_detection,
                                          'false_detection': false_detection,
                                          'not_detected': not_detected,
                                          'true_positive': len(true_detection),
                                          'positive': len(detected_poles),
                                          'groundtruth_count':len(ground_truth),
                                          'precision': len(true_detection) / (len(detected_poles) + EPS),
                                          'recall': len(true_detection) / (len(ground_truth) + EPS)}



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('groundtruth_path')
    parser.add_argument('detection_result_directory')
    args = parser.parse_args()
    eva = DetectionEvaluator(args.groundtruth_path, args.detection_result_directory)
    true_positive = 0
    positive = 0
    groundtruth_count = 0
    for e in eva.detection_map.values():
        true_positive += e['true_positive']
        positive += e['positive']
        groundtruth_count += e['groundtruth_count']
    print('precision=%f, recall=%f' % (true_positive/positive, true_positive/groundtruth_count))
