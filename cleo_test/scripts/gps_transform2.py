import os
import matplotlib.pyplot as plt
from matplotlib.image import imread
import json
import math
from math import sin, cos, sqrt, atan2, radians, degrees, asin
import socket

# Assuming the configuration file path is accessible and correct
config_file_path = 'odlc_config.json'  # Update this path

# Load configuration
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Configuration parameters for sensor dimensions and focal length
sensor_width = config['SENSOR_WIDTH']
sensor_height = config['SENSOR_HEIGHT']
focal_length = config['FOCAL_LENGTH']

def calculate_gsd(altitude, sensor_dim, focal_length, image_dim):
    """
    Calculate the Ground Sample Distance (GSD).
    """
    return (altitude * sensor_dim) / (focal_length * image_dim)

def calculate_destination(lat1_deg, long1_deg, d_km, theta_deg):
    """
    Calculate destination coordinates given starting point, distance, and bearing.
    """
    # Earth's radius in kilometers
    R = 6371.0
    lat1 = radians(lat1_deg)
    long1 = radians(long1_deg)
    theta = radians(theta_deg)
    
    lat2 = asin(sin(lat1) * cos(d_km / R) + cos(lat1) * sin(d_km / R) * cos(theta))
    long2 = long1 + atan2(sin(theta) * sin(d_km / R) * cos(lat1), cos(d_km / R) - sin(lat1) * sin(lat2))
    
    return degrees(lat2), degrees(long2)

def process_image(filename, all_waypoints, base_filename):
    """
    Process each image for clicking and calculating coordinates.
    """
    parts = base_filename[:-4].split('_')
    lat, lon, altitude, drone_yaw = map(float, parts)
    altitude = altitude  # Now using altitude from filename
    drone_yaw = drone_yaw  # Now using drone yaw from filename

    image = imread(filename)
    image_height, image_width, _ = image.shape
    fig, ax = plt.subplots()
    ax.imshow(image)

    def onclick(event):
        ix, iy = event.xdata, event.ydata
        gsd = calculate_gsd(altitude, sensor_width, focal_length, image_width)
        
        # Calculate pixel offsets from image center
        pixel_offset_x = ix - (image_width / 2)
        pixel_offset_y = (image_height / 2) - iy
        
        # Convert pixel offsets to meters using GSD
        offset_x_meters = pixel_offset_x * gsd
        offset_y_meters = pixel_offset_y * gsd
        
        # Calculate distance in meters and convert to kilometers
        distance_km = sqrt(offset_x_meters**2 + offset_y_meters**2) / 1000
        
        # Bearing calculation adjusted with drone_yaw
        bearing_deg = degrees(atan2(offset_x_meters, offset_y_meters))
        
        # Calculate new coordinates considering drone_yaw
        clicked_lat, clicked_lon = calculate_destination(lat, lon, distance_km, bearing_deg + drone_yaw)
        
        all_waypoints.append({"latitude": clicked_lat, "longitude": clicked_lon})
        plt.close(fig)

    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()


def send_data(data, host, port):
    """
    Send data to the specified server.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(json.dumps(data).encode('utf-8'))
        s.sendall("END_OF_DATA".encode('utf-8'))
        

folder_path = "../images" 
waypoints = []

for filename in os.listdir(folder_path):
    if filename.endswith(".jpg"):
        base_filename = os.path.basename(filename)
        process_image(os.path.join(folder_path, filename), waypoints, base_filename)

data_to_send = {"waypoints": waypoints}
print(waypoints)
# host = config["GCS_SERVER_IP"]
# port = config["AIRDROPS_PORT"]

# send_data(data_to_send, host, port)