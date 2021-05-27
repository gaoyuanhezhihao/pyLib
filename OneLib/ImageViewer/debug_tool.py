from shapely.geometry import Polygon
from matplotlib import pyplot as plt

def paint_points(points):
    xs, ys = zip(*points)
    xs, ys = map(list, [xs, ys])
    xs.append(xs[0])
    ys.append(ys[0])
    plt.plot(xs, ys)

def paint_polygons(*polygons):
    for p in polygons:
        paint_points(ToPoints(p))


def ToPoints(polygon):
    points = [p for p in polygon.exterior.coords]
    return points
