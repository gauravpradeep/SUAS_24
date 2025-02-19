import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
import pyproj
import json

def distance(point1, point2):
    return np.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def ant_colony_optimization(points, n_ants, n_iterations, alpha, beta, evaporation_rate, Q):
    n_points = len(points)
    pheromone = np.ones((n_points, n_points))
    best_path = None
    best_path_length = np.inf
    
    for iteration in range(n_iterations):
        paths = []
        path_lengths = []
        
        for ant in range(n_ants):
            visited = [False] * n_points
            current_point = np.random.randint(n_points)
            visited[current_point] = True
            path = [current_point]
            path_length = 0
            
            while False in visited:
                unvisited = np.where(np.logical_not(visited))[0]
                probabilities = np.zeros(len(unvisited))
                
                for i, unvisited_point in enumerate(unvisited):
                    probabilities[i] = pheromone[current_point, unvisited_point]**alpha / distance(points[current_point], points[unvisited_point])**beta
                
                probabilities /= np.sum(probabilities)
                
                next_point = np.random.choice(unvisited, p=probabilities)
                path.append(next_point)
                path_length += distance(points[current_point], points[next_point])
                visited[next_point] = True
                current_point = next_point
            
            paths.append(path)
            path_lengths.append(path_length)
            
            if path_length < best_path_length:
                best_path = path
                best_path_length = path_length
        
        pheromone *= evaporation_rate
        
        for path, path_length in zip(paths, path_lengths):
            for i in range(n_points-1):
                pheromone[path[i], path[i+1]] += Q/path_length
            pheromone[path[-1], path[0]] += Q/path_length
    
    return best_path

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
# best_path = ant_colony_optimization(aco_centroids, n_ants=len(aco_centroids), n_iterations=1500, alpha=1, beta=1, evaporation_rate=0.6, Q=1)
# print(best_path)
best_path=[5, 6, 7, 3, 2, 1, 0, 4, 8, 9, 10, 14, 13, 12, 11, 15, 16, 17, 20, 19, 18, 21, 22, 23]
final_centroids=[]
for i in range(24):
    final_centroids.append(aco_centroids[best_path[i]])

print(final_centroids)
def utm_to_gps(utm_proj, utm_x, utm_y):
    gps_proj = pyproj.Proj(proj='latlong', datum='WGS84')
    lon, lat = pyproj.transform(utm_proj, gps_proj, utm_x, utm_y)
    return lat, lon

# Convert the UTM centroids to GPS coordinates
gps_centroids = [utm_to_gps(utm_proj, point[0], point[1]) for point in final_centroids]
gps_centroids_dict = {"waypoints": [{"latitude": lat, "longitude": lon, "altitude": 50 } for lat, lon in gps_centroids]}

# File path for the JSON file
json_file_path = 'aco_centroids.json'

# Write the GPS centroids to a JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(gps_centroids_dict, json_file, indent=4)