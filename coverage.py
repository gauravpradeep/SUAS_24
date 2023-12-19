import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
import pyproj
import random
import json
latitudes = [13.347815, 13.347632, 13.347639, 13.347818, 13.347815]
longitudes = [74.792147, 74.792138, 74.792246, 74.792201, 74.792147]

points = list(zip(longitudes, latitudes))

utm_proj = pyproj.Proj(proj='utm', zone=18, ellps='WGS84')
utm_points = [utm_proj(lon, lat) for lon, lat in points]

polygon = Polygon(utm_points)
cell_width = 5
cell_height = 5
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

def utm_to_gps(utm_proj, utm_x, utm_y):
    gps_proj = pyproj.Proj(proj='latlong', datum='WGS84')
    lon, lat = pyproj.transform(utm_proj, gps_proj, utm_x, utm_y)
    return lat, lon

# Convert the UTM centroids to GPS coordinates
gps_centroids = [utm_to_gps(utm_proj, point.x, point.y) for point in centroids]
gps_centroids_dict = {"waypoints": [{"latitude": lat, "longitude": lon, "altitude": 50 } for lat, lon in gps_centroids]}

# File path for the JSON file
json_file_path = 'test_centroids.json'

# Write the GPS centroids to a JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(gps_centroids_dict, json_file, indent=4)
