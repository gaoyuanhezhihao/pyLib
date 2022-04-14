import cv2
import argparse
import numpy as np

COLOR_MAPS = [
    (129, 189, 201), (42, 42, 165),
    (255, 191, 41),  (81, 0, 81),
    (65, 163, 0),    (153, 153, 153),
    (232, 35, 244),  (0, 166, 6),
    (142, 0, 0),     (200, 140, 140),
    (0, 220, 220),   (201, 122, 18),
    (30, 170, 250),  (140, 150, 230),
    (60, 20, 220),   (161, 79, 255),
    (0, 0, 255),     (100, 100, 150),
    (70, 70, 70),    (90, 120, 150),
    (60, 20, 220),   (0, 132, 255),
    (255, 255, 255), (0, 255, 255),
    (128, 128, 200), (255, 255, 255),
    (70, 0, 0),      (0, 255, 251),
    (180, 130, 70),  (230, 218, 0),
    (10, 112, 255),  (255, 0, 149),
    (30, 170, 0),    (128, 255, 255),
    (30, 0, 250),    (255, 255, 0),
    (220, 220, 220), (170, 170, 170),
    (142, 0, 0),     (30, 170, 100),
    (40, 40, 40),    (255, 162, 0),
    (170, 170, 170), (142, 0, 0),
    (170, 170, 170), (100, 170, 210),
    (153, 153, 153), (128, 128, 128),
    (142, 0, 0),     (30, 170, 250),
    (192, 192, 192), (0, 220, 220),
    (180, 165, 180), (32, 11, 119),
    (142, 0, 0),     (100, 60, 0),
    (136, 181, 13),  (90, 0, 0),
    (230, 0, 0),     (100, 80, 0),
    (64, 64, 128),   (110, 0, 0),
    (70, 0, 0),      (192, 0, 0),
    (32, 32, 32),    (0, 0, 0)]

def visualize_pose(im_gray):
    im_color = np.zeros((*im_gray.shape, 3), dtype=np.uint8)
    for r in range(im_gray.shape[0]):
        for c in range(im_gray.shape[1]):
            if im_gray[r][c] == 5:
                im_color[r][c] = (255, 255, 255)
    cv2.imshow("pole_pixels", im_color)
    # cv2.waitKey(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    args = parser.parse_args()
    im_gray = cv2.imread(args.image, cv2.IMREAD_GRAYSCALE)
    visualize_pose(im_gray)
    im_color = np.zeros((*im_gray.shape, 3), dtype=np.uint8)
    for r in range(im_gray.shape[0]):
        for c in range(im_gray.shape[1]):
            im_color[r][c] = COLOR_MAPS[im_gray[r][c]]

    cv2.imshow("segmentation_color_image", im_color)
    cv2.waitKey(0)

