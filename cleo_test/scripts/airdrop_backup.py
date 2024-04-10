import os
import matplotlib.pyplot as plt
from matplotlib.image import imread
import json
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
    return (altitude * sensor_dim) / (focal_length * image_dim)

def extract_metadata_from_filename(filename):
    """
    Extract latitude, longitude, altitude, and yaw from the filename.
    Assumes the filename format is 'lat_lon_alt_yaw_x.jpg'.
    """
    base_name = os.path.basename(filename)
    parts = base_name.split('_')
    latitude = float(parts[0])
    longitude = float(parts[1])
    altitude = float(parts[2])
    yaw = float(parts[3][:-4])
    return latitude, longitude, altitude, yaw
    
def process_image(filename):
    """
    Display an image, capture a click, and return the image data including
    the clicked coordinates and the image's original data (latitude, longitude, yaw).
    """
    latitude, longitude, altitude, yaw = extract_metadata_from_filename(filename)
    if yaw<0:
        yaw+=360
    # altitude = altitude - 86
    # print(altitude)
    altitude = config["ALTITUDE"]
    image = imread(filename)
    image_height, image_width, _ = image.shape
    fig, ax = plt.subplots()
    ax.imshow(image)
    
    clicked_coords = []

    def onclick(event):
        ix, iy = event.xdata, event.ydata
        clicked_coords.append((ix, iy))
        plt.close(fig)

    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

    if clicked_coords:
        ix, iy = clicked_coords[0]
        pixel_offset_x = ix - (image_width / 2)
        pixel_offset_y = (image_height / 2) - iy
        gsdW = calculate_gsd(altitude, sensor_width, focal_length, image_width)
        gsdH = calculate_gsd(altitude, sensor_height, focal_length, image_height)
        gsd=max(gsdW,gsdH)
        print(gsdW, gsdH)
        # print()
        offset_x_meters = pixel_offset_x * gsdW
        offset_y_meters = pixel_offset_y * gsdH
        angle_rad = atan2(offset_x_meters,offset_y_meters)
        angle_deg = degrees(angle_rad)
        if angle_deg<0:
            angle_deg+=360
        
        return {
            'latitude': latitude,
            'longitude': longitude,
            'yaw': yaw,
            'x_coordinate': offset_x_meters,
            'y_coordinate': offset_y_meters
        }
    else:
        return None

folder_path = "../images/bigdrone" 
data = []

for filename in os.listdir(folder_path):
    if filename.endswith(".jpg"):
        full_path = os.path.join(folder_path, filename)
        image_data = process_image(full_path)
        if image_data:
            data.append(image_data)

def send_data(data, host, port):
    """
    Send data to the specified server.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(json.dumps(data).encode('utf-8'))
        s.sendall("END_OF_DATA".encode('utf-8'))
        
data_to_send = {"waypoints": data}
with open('image_data.json', 'w') as json_file:
    json.dump(data_to_send, json_file, indent=4)
    
print(data_to_send)
# host = config["GCS_SERVER_IP"]
# port = config["AIRDROPS_PORT"]

# send_data(data_to_send, host, port)