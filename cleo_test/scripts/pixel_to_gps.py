import os
import matplotlib.pyplot as plt
from matplotlib.image import imread
import json
import math
from math import sin, cos, sqrt, atan2, radians, degrees, asin
import socket

config_file_path = 'odlc_config.json' 

with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

sensor_width = config['SENSOR_WIDTH']
sensor_height = config['SENSOR_HEIGHT']
focal_length = config['FOCAL_LENGTH']

def calculate_gsd(altitude, sensor_dim, focal_length, image_dim):
    """
    Calculate the Ground Sample Distance (GSD).
    """
    return (altitude * sensor_dim) / (focal_length * image_dim*100)

def calculate_destination(lat1_deg, long1_deg, d_km, theta_deg):
    """
    Calculate destination coordinates given starting point, distance, and bearing.
    """
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
    altitude = altitude  
    drone_yaw = drone_yaw
    if drone_yaw<0:
        drone_yaw+=360 

    image = imread(filename)
    image_height, image_width, _ = image.shape
    fig, ax = plt.subplots()
    ax.imshow(image)

    def onclick(event):
        ix, iy = event.xdata, event.ydata
        gsdW = calculate_gsd(altitude, sensor_width, focal_length, image_width)
        gsdH = calculate_gsd(altitude, sensor_height, focal_length, image_height)
        print(f"gsdW: {gsdW} m/px, gsdH: {gsdH} m/px")
        
        pixel_offset_x = ix - (image_width / 2)
        pixel_offset_y = (image_height / 2) - iy
        
        offset_x_meters = pixel_offset_x * gsdW
        offset_y_meters = pixel_offset_y * gsdH
        angle_rad = atan2(offset_x_meters,offset_y_meters)
        angle_deg = degrees(angle_rad)
        if angle_deg<0:
            angle_deg+=360
            
        distance_km = sqrt(offset_x_meters**2 + offset_y_meters**2) / 1000
        print(f"Distance from drone: {distance_km} km")
        print(f"Angle from the vertical axis: {angle_deg:.2f} degrees")
        print(f"Global heading from current lat_lon {(angle_deg+drone_yaw)%360}")
        clicked_lat, clicked_lon = calculate_destination(lat, lon, distance_km, (angle_deg + drone_yaw)%360)
        print(f"Clicked lat: {clicked_lat}, lon: {clicked_lon}")
        
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