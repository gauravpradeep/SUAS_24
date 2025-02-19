import itertools
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
import pyproj

def calculate_distance(point1, point2):
    # Assuming points are represented as (x, y) tuples
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

def total_distance(path, points):
    distance = 0
    for i in range(len(path) - 1):
        distance += calculate_distance(points[path[i]], points[path[i + 1]])
    # Add the distance from the last point back to the starting point
    distance += calculate_distance(points[path[-1]], points[path[0]])
    return distance

def brute_force_tsp(points):
    n = len(points)
    # Generate all possible permutations of the points
    all_permutations = itertools.permutations(range(n))
    i=0
    min_distance = float('inf')
    best_path = None
    print((all_permutations))
    # Iterate through all permutations and calculate the total distance
    for permutation in all_permutations:
        i+=1
        print(i)
        distance = total_distance(permutation, points)
        if distance < min_distance:
            min_distance = distance
            best_path = permutation

    return best_path, min_distance

# Example usage:
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

aco_centroids=[]
for pnt in centroids:
    aco_centroids.append([float(pnt.x),float(pnt.y)])
    
    
best_path, min_distance = brute_force_tsp(aco_centroids)
print("Best Path:", best_path)
print("Min Distance:", min_distance)
