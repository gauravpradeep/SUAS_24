import os
import matplotlib.pyplot as plt
from matplotlib.image import imread
import json
import math
import socket

# Assuming the configuration file path is accessible and correct
config_file_path = 'odlc_config.json'  # Update this path

# Load configuration
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Configuration parameters
focal_length = config['FOCAL_LENGTH']
sensor_width = config['SENSOR_WIDTH']
sensor_height = config['SENSOR_HEIGHT']
altitude = config['ALTITUDE']
# drone_yaw = config['DRONE_YAW']  # Assuming drone yaw is provided in the configuration
drone_yaw=0

def calculate_gsd(altitude, sensor_dim, focal_length, image_dim):
    """
    Calculate the Ground Sample Distance (GSD).
    """
    return (altitude * sensor_dim) / (focal_length * image_dim)

def adjust_for_yaw(offset_x_meters, offset_y_meters, drone_yaw):
    """
    Adjust the offsets for the drone's yaw.
    """
    drone_yaw_rad = math.radians(drone_yaw)
    rotated_offset_x = offset_x_meters * math.cos(drone_yaw_rad) - offset_y_meters * math.sin(drone_yaw_rad)
    rotated_offset_y = offset_x_meters * math.sin(drone_yaw_rad) + offset_y_meters * math.cos(drone_yaw_rad)
    return rotated_offset_x, rotated_offset_y

def calculate_new_coordinates(lat, lon, offset_x_meters, offset_y_meters):
    """
    Calculate new geographic coordinates.
    """
    lat_offset = offset_y_meters / 111319
    lon_offset = offset_x_meters / (111319 * math.cos(math.radians(lat)))
    new_lat = lat + lat_offset
    new_lon = lon + lon_offset
    return new_lat, new_lon

def process_image(filename, all_waypoints, base_filename):
    """
    Process each image for clicking and calculating coordinates.
    """
    lat, lon = map(float, base_filename[:-4].split('_'))

    image = imread(filename)
    image_height, image_width, _ = image.shape
    fig, ax = plt.subplots()
    ax.imshow(image)

    def onclick(event):
        ix, iy = event.xdata, event.ydata
        gsd_width = calculate_gsd(altitude, sensor_width, focal_length, image_width)
        gsd_height = calculate_gsd(altitude, sensor_height, focal_length, image_height)
        
        offset_x = (ix - (image_width / 2)) * gsd_width
        offset_y = (iy - (image_height / 2)) * gsd_height
        
        adjusted_offset_x, adjusted_offset_y = adjust_for_yaw(offset_x, offset_y, drone_yaw)
        clicked_lat, clicked_lon = calculate_new_coordinates(lat, lon, adjusted_offset_x, adjusted_offset_y)
        
        all_waypoints.append({"latitude": clicked_lat, "longitude": clicked_lon})
        plt.close(fig)

    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

# def send_data(data, host, port):
#     """
#     Send data to the specified server.
#     """
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((host, port))
#         s.sendall(json.dumps(data).encode('utf-8'))
#         s.sendall("END_OF_DATA".encode('utf-8'))

folder_path = "../images"  # Update this path
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
