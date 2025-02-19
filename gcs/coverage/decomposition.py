
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
import pyproj
import random

latitudes = [38.31442311312976, 38.31421041772561, 38.31440703962630, 38.31461622313521, 38.31442311312976]
longitudes = [-76.54522971451763, -76.54400246436776, -76.54394394383165, -76.54516993186949, -76.54522971451763]

points = list(zip(longitudes, latitudes))

utm_proj = pyproj.Proj(proj='utm', zone=18, ellps='WGS84')
utm_points = [utm_proj(lon, lat) for lon, lat in points]

polygon = Polygon(utm_points)
cell_width = 16.5
cell_height = 11.03
centroids=[]
# Determine the bounding box of the polygon.
min_x, min_y, max_x, max_y = polygon.bounds

# Create a grid of rectangular cells.
cells = []
x = min_x
while x < max_x:
    y = min_y
    while y < max_y:
        cell = Polygon([(x, y), (x + cell_width, y), (x + cell_width, y + cell_height), (x, y + cell_height)])
        intersection = polygon.intersection(cell)
        if not intersection.is_empty and not isinstance(intersection, Point):
            cells.append(cell)
            centroids.append(cell.centroid)
        y += cell_height
    x += cell_width

# Visualize the cells and the polygon (optional).
fig, ax = plt.subplots()
for i, cell in enumerate(cells):
    x, y = cell.exterior.xy
    ax.fill(x, y, alpha=0.5, edgecolor='black')
x, y = polygon.exterior.xy
ax.plot(x, y, color='red')
ax.set_aspect('equal')
plt.show()
print(centroids)