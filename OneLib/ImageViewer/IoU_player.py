import sys
sys.path = ['/home/zhihaohe/.local/lib/python3.5/site-packages/'] + sys.path
import argparse
import os
from os.path import splitext
import cv2

from images_player import ImageMap
from player_ui import PlayerUI
from evaluate_detection import DetectionEvaluator

green = (0, 128, 0)
lime =(0, 255, 0)
red = (0, 0, 255)
blue = (255, 0, 0)
yellow = (51, 230, 255)


def to_point2i(pt):
    return int(pt[0]), int(pt[1])

def paint_pole(image, p, color):
    cv2.line(image, to_point2i(p[0][0]), to_point2i(p[0][1]), color, 1)
    cv2.line(image, to_point2i(p[0][1]), to_point2i(p[1][1]), color, 1)
    cv2.line(image, to_point2i(p[1][1]), to_point2i(p[1][0]), color, 1)
    cv2.line(image, to_point2i(p[1][0]), to_point2i(p[0][0]), color, 1)

class ImageIOU_Fetcher(ImageMap):

    def __init__(self, image_dir, evaluation):
        self.evaluation = evaluation
        super().__init__(image_dir)
        # load gt

    def update_jobs(self):
        print("update_jobs i=", self.i_)
        super().update_jobs()
        name = splitext(self.fnames_[self.i_])[0]
        # paint poles to image
        image = self.get_image()
        for p, g in self.evaluation[name]['true_detection']:
            paint_pole(image, p, green)
            paint_pole(image, g, blue)
        for p in self.evaluation[name]['false_detection']:
            paint_pole(image, p, red)
        for p in self.evaluation[name]['not_detected']:
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
    p.add_argument('detection_directory')
    p.add_argument('groundtruth_path')
    args = p.parse_args()
    evaluation = DetectionEvaluator(
                       args.groundtruth_path, args.detection_directory)
    fetcher = ImageIOU_Fetcher(args.image_directory, evaluation)
    ui = PlayerUI(fetcher)
    ui.run()

