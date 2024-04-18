import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
import pyproj

def distance(point1, point2):
    return np.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def count_turns(path):
    # Count the number of turns in the path
    turns = 0
    for i in range(len(path)-2):
        x1, y1 = path[i]
        x2, y2 = path[i+1]
        x3, y3 = path[i+2]
        
        cross_product = (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)
        if cross_product != 0:
            turns +=1
    
    return turns

def ant_colony_optimization(points, start_vertex, n_ants, n_iterations, alpha, beta, evaporation_rate, Q):
    n_points = len(points)
    pheromone = np.ones((n_points, n_points))
    best_path = None
    best_path_length = np.inf
    best_path_turns = np.inf
    
    for iteration in range(n_iterations):
        paths = []
        path_lengths = []
        indices=[]
        for ant in range(n_ants):
            visited = [False] * n_points
            current_point = start_vertex  # Fixed starting vertex
            visited[current_point] = True
            path = [points[current_point]]
            path_length = 0
            
            while False in visited:
                unvisited = np.where(np.logical_not(visited))[0]
                probabilities = np.zeros(len(unvisited))
                
                for i, unvisited_point in enumerate(unvisited):
                    probabilities[i] = (pheromone[current_point, unvisited_point]**alpha /
                                        distance(points[current_point], points[unvisited_point])**beta)
                
                probabilities /= np.sum(probabilities)
                
                next_point = np.random.choice(unvisited, p=probabilities)
                path.append(points[next_point])
                indices.append(next_point)
                path_length += distance(points[current_point], points[next_point])
                visited[next_point] = True
                current_point = next_point
            
            paths.append(path)
            path_lengths.append(path_length)
            
            if path_length < best_path_length:
                best_path = path
                best_path_length = path_length
                best_path_turns = count_turns(path)
            elif path_length == best_path_length and count_turns(path) < best_path_turns:
                best_path = path
                best_path_turns = count_turns(path)
        
        pheromone *= evaporation_rate
        
        for path, path_length in zip(paths, path_lengths):
            turns = count_turns(path)
            for i in range(len(path)-1):
                point_index1 = aco_centroids.index(path[i])
                point_index2 = aco_centroids.index(path[i+1])
                pheromone[point_index1, point_index2] += Q / (path_length + turns)  # Updated pheromone update rule
                pheromone[point_index2, point_index1] += Q / (path_length + turns)
    return best_path

# Rest of the code remains unchanged
latitudes = [38.31442311312976, 38.31421041772561, 38.31440703962630, 38.31461622313521, 38.31442311312976]
longitudes = [-76.54522971451763, -76.54400246436776, -76.54394394383165, -76.54516993186949, -76.54522971451763]

points = list(zip(longitudes, latitudes))

utm_proj = pyproj.Proj(proj='utm', zone=18, ellps='WGS84')
utm_points = [utm_proj(lon, lat) for lon, lat in points]

polygon = Polygon(utm_points)
cell_width = 16.5
cell_height = 11.03
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

aco_centroids=[]
for pnt in centroids:
    aco_centroids.append([float(pnt.x), float(pnt.y)])
start_vertex = 1  # Specify the fixed starting vertex
best_path = ant_colony_optimization(aco_centroids, start_vertex, n_ants=150, n_iterations=500, alpha=3, beta=3, evaporation_rate=0.8, Q=1)
print(best_path)
final_centroids=best_path
x_coords = [point[0] for point in final_centroids]
y_coords = [point[1] for point in final_centroids]

# Plot the optimized path with labels
plt.figure(figsize=(8, 6))
plt.plot(x_coords + [x_coords[0]], y_coords + [y_coords[0]], marker='o', linestyle='-', color='r', linewidth=2, label='Optimized Path')

# Scatter plot with labels
for i, txt in enumerate(range(1, len(final_centroids)+1)):
    plt.annotate(txt, (x_coords[i], y_coords[i]), textcoords="offset points", xytext=(0, 5), ha='center')

plt.scatter(x_coords, y_coords, c='r', marker='o', label='Centroids')
plt.title('Optimized Path with Labels')
plt.xlabel('UTM X Label')
plt.ylabel('UTM Y Label')
plt.legend()
plt.show()
# Visualization code (unchanged)
