import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
import pyproj
import json

def utm_to_gps(utm_proj, utm_x, utm_y):
    gps_proj = pyproj.Proj(proj='latlong', datum='WGS84')
    lon, lat = pyproj.transform(utm_proj, gps_proj, utm_x, utm_y)
    return lat, lon

# Read boundary coordinates from JSON file
json_file_path = 'ground_testing.json'  # Specify the path to your JSON file
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

latitudes = [point['latitude'] for point in data['waypoints']]
longitudes = [point['longitude'] for point in data['waypoints']]

points = list(zip(longitudes, latitudes))

utm_proj = pyproj.Proj(proj='utm', zone=18, ellps='WGS84')
utm_points = [utm_proj(lon, lat) for lon, lat in points]

polygon = Polygon(utm_points)
cell_width = 15
cell_height = 10
centroids=[]

min_x, min_y, max_x, max_y = polygon.bounds

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

fig, ax = plt.subplots()
for i, cell in enumerate(cells):
    x, y = cell.exterior.xy
    ax.fill(x, y, alpha=0.5, edgecolor='black')
x, y = polygon.exterior.xy
ax.plot(x, y, color='red')
ax.set_aspect('equal')
plt.show()

gps_centroids = [utm_to_gps(utm_proj, point.x, point.y) for point in centroids]
gps_centroids_dict = {"waypoints": [{"latitude": lat, "longitude": lon, "altitude": 45} for lat, lon in gps_centroids]}

# Write the GPS centroids to a JSON file
output_json_file_path = 'coverage_waypoints.json'  # Specify the path to save the output JSON file
with open(output_json_file_path, 'w') as output_json_file:
    json.dump(gps_centroids_dict, output_json_file, indent=4)
