import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import pyproj
import random

# Define the 5 sets of latitude and longitude points to form a closed polygon
latitudes = [38.31442311312976, 38.31421041772561, 38.31440703962630, 38.31461622313521, 38.31442311312976]
longitudes = [-76.54522971451763, -76.54400246436776, -76.54394394383165, -76.54516993186949, -76.54522971451763]

# Create a list of tuples with latitude and longitude values
points = list(zip(longitudes, latitudes))

# Initialize the UTM projection (for zone 18T, Western Maryland)
utm_proj = pyproj.Proj(proj='utm', zone=18, ellps='WGS84')

# Convert GPS coordinates to UTM coordinates
utm_points = [utm_proj(lon, lat) for lon, lat in points]

# Create a Shapely polygon from the UTM coordinates
polygon = Polygon(utm_points)

# Determine the number of squares to create (20 in this case)
num_squares = 20

# Create a list to store the squares
squares = []

# Calculate the bounds of the polygon
min_x, min_y, max_x, max_y = polygon.bounds

# Calculate the size of each square
square_size = (max_x - min_x) / num_squares

# Divide the polygon into squares
for i in range(num_squares):
    left_x = min_x + i * square_size
    right_x = left_x + square_size
    square = Polygon([(left_x, min_y), (right_x, min_y), (right_x, max_y), (left_x, max_y)])
    intersection = polygon.intersection(square)
    if not intersection.is_empty:
        # Generate a random color for each square
        squares.append(intersection)

# Create a 2D plot
plt.figure()

# Plot the original polygon in blue
plt.plot(*polygon.exterior.xy, marker='o', linestyle='-', color='blue', label="Original Polygon")

# Plot every 4th square in a different color
for i, square in enumerate(squares):
    plt.plot(*square.exterior.xy, marker='o', linestyle='-', color='red', alpha=1)  # Highlight every 4th square

plt.plot(*polygon.exterior.xy, marker='o', linestyle='-', color='blue', label="Original Polygon")
plt.xlabel("Easting (m)")
plt.ylabel("Northing (m)")
plt.title("All 20 Squares with Every 4th Square Highlighted in UTM Coordinates")
plt.legend()

# Show the 2D plot
plt.grid(True)
plt.show()
