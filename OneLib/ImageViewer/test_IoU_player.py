import pytest
from evaluate_detection import parse_gt, parse_gt_pole, calculate_iou_of_bbox, area_of_bbox, bbox_of_pole, parse_pole, calculate_iou_of_poles


def test_parse_gt_pole():
    s = "178.15,464.53;179.70,609.85;187.13,608.82;185.23,465.39"
    pole = ((178.15,464.53), (179.70,609.85)), ((185.23,465.39), (187.13,608.82))
    assert pole == parse_gt_pole(s)


def test_parse_gt():
    gt_map = parse_gt('./test_data/annotations.xml')
    assert 'guimiao-night_0' in gt_map
    assert 5 == len(gt_map['guimiao-night_0'])
    pole1 = gt_map['guimiao-night_0'][0]
    assert 2 == len(pole1)
    left, right = pole1
    assert left[0][0] == pytest.approx(178.15)
    assert left[0][1] == pytest.approx(464.53)
    assert left[1][0] == pytest.approx(179.70)
    assert left[1][1] == pytest.approx(609.85)

def test_iou():
    b1 = (1, 1), (3, 4)
    b2 = (1, 2), (3, 5)
    assert pytest.approx(4.0 /8.0) == calculate_iou_of_bbox(b1, b2)

def test_area_of_bbox():
    pole = (1, 1), (3, 4)
    assert pytest.approx(6) == area_of_bbox(pole)


def test_bbox_of_pole():
    pole = ((1, 1), (1, 4)), ((3, 1), (3, 4))
    bbox = (1, 1), (3, 4)
    assert bbox_of_pole(pole) == bbox


def test_bbox_of_pole_2():
    pole = ((3.5, 2.5), (2.5, 6.5)), ((4.5, 6.7), (5.5, 2.5))
    bbox = ((2.5, 2.5), (5.5, 6.7))
    assert bbox_of_pole(pole) == bbox

def test_parse_pole_detection():
    pole = parse_pole('(88.4806,529.004)--(89.8054,580.028) | (102.372,537.977)--(101.829,575.998)')
    assert pole[0] == ((88.4806,529.004), (89.8054,580.028))

def test_parse_pole_detection2():
    pole = parse_pole('(88,529)--(89.8054,580.028) | (102.372,537.977)--(101.829,575.998)')
    assert pole[0] == ((88.,529.), (89.8054,580.028))

def test_parse_pole_detection3():
    pole = parse_pole('(3.34392e-06,696)--(-3.34392e-06,849) | (13.1554,696)--(8.14999,849)')
    assert pole[0][0][0] == pytest.approx(3.34392e-6)

def test_iou_of_poles():
    pole1 = (((2, 0), (0, 4)), ((4, 0), (5, 4)))
    pole2 = (((4, 3), (4, 7)), ((6, 3), (6, 7)))
    assert pytest.approx(0.875 / (14 + 8 - 0.875)) == calculate_iou_of_poles(pole1, pole2)
